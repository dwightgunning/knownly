import json, StringIO
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import View, TemplateView, RedirectView
from django.views.generic.edit import BaseFormView, FormMixin
from dropbox.client import DropboxClient, DropboxOAuth2Flow
from dropbox.rest import ErrorResponse

from knownly.console.forms import WebsiteForm
from knownly.console.models import DropboxUser, DropboxSite

class IndexView(TemplateView):
	dropbox_user = None

	def get(self, request, *args, **kwargs):
		if 'dropbox_user' in self.request.session:
			self.dropbox_user = DropboxUser.objects.get(pk=self.request.session['dropbox_user'])

			if self.dropbox_user.dropbox_token:
				client = DropboxClient(self.dropbox_user.dropbox_token)
				try:
					account_info = client.account_info()
					self.dropbox_user.display_name = account_info["display_name"]
					self.dropbox_user.email = account_info["email"]
					self.dropbox_user.save()
				except ErrorResponse, e:
					# Remove the dead user_access token
					self.dropbox_user.access_token = ''
					self.dropbox_user.save()
					self.dropbox_user = None

					del self.request.session['dropbox_user']

					# Present a useful error to the user
					message = 'Account authentication error.'
					if e.user_error_message:
						message = '%s %s' % (messages, e.user_error_message)
					messages.add_message(request, messages.ERROR, message)

		return super(IndexView, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)

		if self.dropbox_user:
			context['dropbox_user'] = self.dropbox_user

			if not self.dropbox_user.subscription_active:
				trial_end = self.dropbox_user.account_created + timedelta(days=14)
				time_left = trial_end - timezone.now()
				context['free_days_left'] = time_left.days

			context['websites'] = DropboxSite.objects.filter(dropbox_user=self.dropbox_user)
			context['create_website_form'] = WebsiteForm({'dropboxy_user': self.dropbox_user})
			self.template_name = 'console/index.html'
		else:
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
	dropbox_user = None

	def get_redirect_url(self, **kwargs):
		try:
			token, user_id, url_state = DropboxOAuth2Flow(settings.DROPBOX_APP_KEY, 
												settings.DROPBOX_APP_SECRET, 
												get_redirect_uri(self.request),
                                       			self.request.session, 
                                       			'dropbox-auth-csrf-token').finish(self.request.GET)
			
			self.dropbox_user, created = DropboxUser.objects.get_or_create(user_id=user_id, defaults={'dropbox_token': token})
			if not created:
				self.dropbox_user.dropbox_token = token
				self.dropbox_user.save()
		except DropboxOAuth2Flow.NotApprovedException, e:
			# Present a useful error to the user
			message = 'Dropbox indicated that the request for access was not approved. If this was a mistake just hit the button below to try again.'
			messages.add_message(self.request, messages.WARNING, message)
		except KeyError, e:
			# Present a useful error to the user
			message = 'Account authentication error.'
			if 'dropbox-auth-csrf-token' in e.args:
				message = '%s This is potentially a browser session error. Please refresh the page and try again.' % message
			messages.add_message(self.request, messages.ERROR, message)
		except Exception, e:
			# Present a useful error to the user
			message = 'Account authentication error.'
			messages.add_message(self.request, messages.ERROR, message)

		# Check and if needed, create a placeholder website
		if self.dropbox_user:
			client = DropboxClient(self.dropbox_user.dropbox_token)
			knownly_dir = client.metadata('/')
			if not knownly_dir.get('contents'):
				output = StringIO.StringIO()
				output.write('<html>\n<head>\n  <title>Hello world</title>\n</head>\n<body>\n  <h1>Hello world...</h1>\n</body>\n</html>\n')
				site = None
				for i in range(3):
					try:
						website_domain = '%s.knownly.net' % haiku.haiku()
						site = DropboxSite(dropbox_user=self.dropbox_user, domain=website_domain)
						continue
					except:
						pass

				if site:
					try:
						response = client.put_file('%s/index.html' % website_domain, output)
						site.save()
						message = 'We\'ve created you a placeholder website at <a href="%s">%s</a>.' % (site.domain, site.domain)
						messages.add_message(self.request, messages.SUCCESS, message, extra_tags='safe')					
					except ErrorResponse, e:
						# Present a useful error to the user
						message = 'We attempted to create you a placeholder website but encountered problems.'
						if e.user_error_message:
							message = '%s %s' % (messages, e.user_error_message)
						messages.add_message(self.request, messages.ERROR, message)
				else:
					# Present a useful error to the user
					message = 'We attempted to create you a placeholder website but encountered problems.'
					messages.add_message(self.request, messages.ERROR, message)


			self.request.session['dropbox_user'] = self.dropbox_user.pk

		return reverse('index')


class LogoutDropboxUserView(RedirectView):

	def get_redirect_url(self, **kwargs):
		try:
			del self.request.session['dropbox_user']
		except KeyError:
			pass

		message = "Thanks for spending some time with us. Hope to see you soon!"
		messages.add_message(self.request, messages.INFO, message)
		return reverse('index')

class CreateWebsiteView(BaseFormView):
	success_url = '/'
	form_class = WebsiteForm
	http_method_names = ['post', 'put', 'options', 'trace']

	def dispatch(self, request, *args, **kwargs):
		try:
			self.dropbox_user = DropboxUser.objects.get(pk=self.request.session['dropbox_user'])
		except DropboxUser.DoesNotExist:
			return HttpResponse('Unauthorized', status=401)

		if not request.is_ajax():
			return HttpResponseBadRequest("Only accepts XHR.")

		return super(CreateWebsiteView, self).dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		form.dropbox_user = self.dropbox_user
		self.object = form.save()
		super(CreateWebsiteView, self).form_valid(form)

		client = DropboxClient(self.dropbox_user.dropbox_token)
		try:
			client.metadata(self.object.domain, file_limit=2)
		except ErrorResponse, e:
			if e.status == 404:
				output = StringIO.StringIO()
				output.write('<html>\n<head>\n  <title>Hello world</title>\n</head>\n<body>\n  <h1>Hello world...</h1>\n</body>\n</html>\n')
				client.put_file('%s/index.html' % self.object.domain, output)

		if self.object.domain.endswith('knownly.net'):
			message = 'Your website is created and immediately active. <a href="%s">Check it out</a>.'
		else:
			message = 'Your website is created although custom domains may need additional DNS configuration. <a href="%s" class="alert-link">Find out more</a>.' % reverse('support')

		return self.render_to_json_response({'domain': self.object.domain, 'message': message})

	def form_invalid(self, form):
		return self.render_to_json_response(form.errors, status=400)

	def render_to_json_response(self, context, **response_kwargs):
		data = json.dumps(context)
		response_kwargs['content_type'] = 'application/json'
		return HttpResponse(data, **response_kwargs)


def get_redirect_uri(request):
	if not settings.DEBUG and request.is_secure:
		protocol = 'https://'
	else:
		protocol = 'http://'

	return '%s%s%s' % (protocol, request.META['HTTP_HOST'], reverse('dropbox_auth_finish'))
