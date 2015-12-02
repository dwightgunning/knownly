import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from dropbox import Dropbox
from mixpanel import Mixpanel

from knownly.celery import app
from knownly.console.models import DropboxSite, DropboxUser

GRACE_MINUTES = 1

logger = logging.getLogger(__name__)


@app.task
def process_dropbox_user_activity(dropbox_token):
    try:
        dropbox_user = DropboxUser.objects.get(dropbox_token=dropbox_token)
    except DropboxUser.DoesNotExist:
        logger.error('Cannot process activity for unrecognised token: %s'
                     % dropbox_token)
        return

    dropbox = Dropbox(dropbox_user.dropbox_token)
    sites = DropboxSite.objects.filter(dropbox_user=dropbox_user)
    time_now = timezone.now()

    for site in sites:
        if time_now < site.date_created + timedelta(minutes=GRACE_MINUTES):
            logger.warning('Ignoring website update received prior'
                           ' to grace period')
            continue

        # Check for an updated cursor
        try:
            # Fetch the latest cursor for the website folder
            response = dropbox.files_list_folder_get_latest_cursor(
                path='/%s' % site.domain, include_media_info=False)
            latest_cursor = response.cursor
        except:
            logger.exception("Error fetching cursor for %s", site.domain)
            continue

        if not site.cursor or site.cursor != latest_cursor:
            site.date_modified = time_now

            if not site.date_activated:
                site.date_activated = time_now

                mp = Mixpanel(settings.MIXPANEL_TOKEN)
                mp.people_set_once(dropbox_user.django_user.email,
                                   {'activated':
                                    site.date_activated.isoformat()})

            site.save()


@app.task
def fetch_website_folder_cursor(dropbox_site_id):
    dropbox_site = DropboxSite.objects.get(id=dropbox_site_id)
    dropbox = Dropbox(dropbox_site.dropbox_user.dropbox_token)

    try:
        # Fetch the latest cursor for the website folder
        response = dropbox.files_list_folder_get_latest_cursor(
            path='/%s' % dropbox_site.domain, include_media_info=False)
        dropbox_site.cursor = response.cursor
        dropbox_site.save()
    except:
        logger.exception("Error fetching cursor for %s", dropbox_site.domain)
