from django.conf import settings
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.urlresolvers import reverse
from django.views.generic import View, TemplateView, RedirectView

from dropbox.client import DropboxClient, DropboxOAuth2Flow

from knownly.console.models import DropboxUser

class IndexView(TemplateView):

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)

		if 'dropbox_user' in self.request.session:
			dropbox_user = DropboxUser.objects.get(pk=self.request.session['dropbox_user'])
			access_token = dropbox_user.dropbox_token

			if access_token:
				client = DropboxClient(access_token)
				account_info = client.account_info()
				dropbox_user.username = account_info["display_name"]
				dropbox_user.save()

				context['dropbox_user'] = dropbox_user
				context['real_name'] = account_info["display_name"]
				self.template_name = 'console/index.html'

				return context
		
		self.template_name = 'console/public.html'
		return context

class DropboxAuthStartView(RedirectView):
	
	def get_redirect_url(self, **kwargs):
		redirect_uri = get_redirect_uri(self.request)
		
		url = DropboxOAuth2Flow(settings.DROPBOX_APP_KEY, 
								settings.DROPBOX_APP_SECRET, 
								get_redirect_uri(self.request),
								self.request.session, 
								'dropbox-auth-csrf-token').start()

		return url

class DropboxAuthCompleteView(RedirectView):

	def get_redirect_url(self, **kwargs):
		try:
			token, user_id, url_state = DropboxOAuth2Flow(settings.DROPBOX_APP_KEY, 
												settings.DROPBOX_APP_SECRET, 
												get_redirect_uri(self.request),
                                       			self.request.session, 
                                       			'dropbox-auth-csrf-token').finish(self.request.GET)

		except DropboxOAuth2Flow.BadRequestException, e:
			raise SuspiciousOperation()
		except DropboxOAuth2Flow.BadStateException, e:
			raise SuspiciousOperation()
		except DropboxOAuth2Flow.CsrfException, e:
			raise PermissionDenied()
		except DropboxOAuth2Flow.NotApprovedException, e:
			raise Exception()
			# flash('Not approved....')
			# return redirect(url_for('home'))
		except DropboxOAuth2Flow.ProviderException, e:
			raise PermissionDenied()

		dropbox_user, created = DropboxUser.objects.get_or_create(user_id=user_id,
																	defaults={'dropbox_token': token})
		if not created:
			dropbox_user.dropbox_token = token
			dropbox_user.save()
		
		self.request.session['dropbox_user'] = dropbox_user.pk

		return reverse('index')


class LogoutDropboxUserView(RedirectView):

	def get_redirect_url(self, **kwargs):
		try:
			del self.request.session['dropbox_user']
		except KeyError:
			pass

		return reverse('index')
		# return super(LogoutDropboxUserView, self).get_redirect_url(**kwargs)


def get_redirect_uri(request):
	if request.is_secure:
		protocol = 'https://' 
	else:
		protocol = 'http://'

	if request.META['SERVER_PORT']:
		port = ':%s' % request.META['SERVER_PORT']
	else:
		port = ''

	if settings.DEBUG:
		port = ':8080'
		protocol = 'http://'

	return '%s%s%s%s' % (protocol, request.META['HTTP_HOST'], port, reverse('dropbox_auth_finish'))
