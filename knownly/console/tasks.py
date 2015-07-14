from datetime import timedelta
import logging
import os

from django.conf import settings
from django.utils import timezone

from dateutil import parser
from dropbox.client import DropboxClient, DropboxOAuth2Flow
from dropbox.rest import ErrorResponse
from mixpanel import Mixpanel

from knownly.console.models import DropboxUser, DropboxSite
from knownly.celery import app

GRACE_MINUTES = 2

logger = logging.getLogger(__name__)

@app.task
def process_dropbox_user_activity(dropbox_user_id):
    dropbox_user = DropboxUser.objects.get(user_id=dropbox_user_id)
    sites = DropboxSite.objects.filter(dropbox_user=dropbox_user)

    client = DropboxClient(dropbox_user.dropbox_token)
    new_activation = False

    for site in sites:
        site_init_cutoff = site.date_created + timedelta(minutes=GRACE_MINUTES)

        if site.dropbox_hash:
            try:
                metadata = client.metadata(path='/%s' % site.domain,
                                           hash=site.dropbox_hash,
                                           include_media_info=False)
                site.hash = metadata.get('hash')
                site.date_modified = timezone.now()

                if not site.date_activated:
                    if timezone.now() >= site_init_cutoff: 
                        site.date_activated = site.date_modified
                        new_activation = site.date_activated
                    elif not site.date_activated:
                        logger.debug('Ignoring website update received prior'
                                    ' to grace period')

                site.save()
            except ErrorResponse, er:
                if er.status != 304:
                    logger.error("Error fetching metadata for %s", site.domain)
        elif timezone.now() >= site_init_cutoff:
            logger.warn("Missing hash on initialised website: %s", site.domain)

    if not dropbox_user.date_activated and new_activation:
        dropbox_user.date_activated = new_activation
        dropbox_user.save()

        mp = Mixpanel(settings.MIXPANEL_TOKEN)
        mp.people_set(dropbox_user.django_user.email,
                      {'activated' : new_activation.isoformat()})

@app.task
def fetch_website_folder_metadata(dropbox_site_id):
    dropbox_site = DropboxSite.objects.get(id=dropbox_site_id)
    client = DropboxClient(dropbox_site.dropbox_user.dropbox_token)

    try:
        # Fetch the metadata for the website folder
        metadata = client.metadata(path='/%s' % dropbox_site.domain,
                                   include_media_info=False)
        dropbox_site.dropbox_hash = metadata.get('hash')
        dropbox_site.date_modified = parser.parse(metadata.get('modified'))
        dropbox_site.save()
    except ErrorResponse, er:
        if er.status != 304:
            logger.error("Error fetching metadata for %s", dropbox_site.domain)
