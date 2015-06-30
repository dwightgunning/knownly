import logging

from django.conf import settings
from django.contrib.auth import get_user_model

from dropbox.client import DropboxClient, DropboxOAuth2Flow
from dropbox.rest import ErrorResponse

from knownly.console.models import DropboxUser

logger = logging.getLogger(__name__)

User = get_user_model()

class DropboxUserService(object):

	def get_or_create(self, user_id, dropbox_token):
		dropbox_user, created = DropboxUser.objects.get_or_create(
			user_id=user_id, defaults={'dropbox_token': dropbox_token})

		if created or not dropbox_user.django_user:
			# Fetch the Dropbox user's account info
			try:
				client = DropboxClient(dropbox_user.dropbox_token)
				account_info = client.account_info()
			except ErrorResponse, e:
				logger.exception('Dropbox API Error')
			else:
				dropbox_user.django_user = self._create_user(account_info)
				dropbox_user.display_name = account_info['display_name']
				dropbox_user.email = account_info['email']
				dropbox_user.save()
		else:
			dropbox_user.dropbox_token = dropbox_token
			dropbox_user.save()

		return dropbox_user, created

	def _create_user(self, account_info):
		email = account_info['email']
		if 'name_details' in account_info:
			first_name = account_info['name_details'].get('given_name')
			last_name = account_info['name_details'].get('surname')
		else:
			first_name = ''
			last_name = ''
		random_password = User.objects.make_random_password()

		if User.objects.filter(username=email).exists():
			user = User.objects.get(username=email)
			user.username=account_info['uid'],
			user.first_name=first_name,
			user.last_name=last_name,
			user.password=random_password
			user.save()
		else:
			return User.objects.create_user(username=account_info['uid'],
											email=email,
											first_name=first_name,
											last_name=last_name,
											password=random_password)

	def check_and_create_sample_website(self, dropbox_user):
		client = DropboxClient(dropbox_user.dropbox_token)
		knownly_dir = client.metadata('/')
		if not knownly_dir.get('contents'):
			output = StringIO.StringIO()
			output.write('<html>\n<head>\n  <title>Hello world</title>\n' 
						 '</head>\n<body>\n  <h1>Hello world...</h1>\n'
						 '</body>\n</html>\n')
			website_domain = '%s.knownly.net' % haiku.haiku()
			site = DropboxSite(dropbox_user=dropbox_user, 
							   domain=website_domain)

			try:
				response = client.put_file('%s/index.html' % website_domain, output)
				site.save()
				# message = 'We\'ve created you a placeholder website at <a href="%s">%s</a>.' % (site.domain, site.domain)
				# messages.add_message(self.request, messages.SUCCESS, message, extra_tags='safe')					
			except ErrorResponse, e:
				# Present a useful error to the user
				logger.exception("Error setting up user's initial website")
