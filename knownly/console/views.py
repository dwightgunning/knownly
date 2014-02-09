import json, logging, StringIO
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.utils import timezone
from django.views.generic import View, TemplateView, RedirectView
from django.views.generic.edit import BaseFormView, FormMixin, DeleteView
from dropbox.client import DropboxClient, DropboxOAuth2Flow
from dropbox.rest import ErrorResponse

from knownly.console import haiku
from knownly.console.forms import WebsiteForm
from knownly.console.models import DropboxUser, DropboxSite, ArchivedDropboxSite

# Get an instance of a logger
logger = logging.getLogger(__name__)

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
					logger.exception("Account authentication problem.")
					# Remove the dead user_access token
					self.dropbox_user.access_token = ''
					self.dropbox_user.save()
					self.dropbox_user = None

					self.request.session.flush()
					self.request.session.cycle_key()

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
			logger.warn("Dropbox OAuth error - app not approved")
			message = 'Dropbox indicated that the request for access was not approved. If this was a mistake just hit the button below to try again.'
			messages.add_message(self.request, messages.WARNING, message)
		except KeyError, e:
			logger.exception("Dropbox OAuth error")
			# Present a useful error to the user
			message = 'Account authentication error.'
			if 'dropbox-auth-csrf-token' in e.args:
				message = '%s This is potentially a browser session error. Please refresh the page and try again.' % message
			messages.add_message(self.request, messages.ERROR, message)
		except Exception, e:
			logger.exception("Dropbox OAuth error")
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
				website_domain = '%s.knownly.net' % haiku.haiku()
				site = DropboxSite(dropbox_user=self.dropbox_user, domain=website_domain)

				try:
					response = client.put_file('%s/index.html' % website_domain, output)
					site.save()
					message = 'We\'ve created you a placeholder website at <a href="%s">%s</a>.' % (site.domain, site.domain)
					messages.add_message(self.request, messages.SUCCESS, message, extra_tags='safe')					
				except ErrorResponse, e:
					# Present a useful error to the user
					logger.exception("Error setting up user's initial website")
					message = 'We attempted to create you a placeholder website but encountered problems.'
					if e.user_error_message:
						message = '%s %s' % (messages, e.user_error_message)
					messages.add_message(self.request, messages.ERROR, message)

			self.request.session['dropbox_user'] = self.dropbox_user.pk

		return reverse('index')


class LogoutDropboxUserView(RedirectView):

	def get_redirect_url(self, **kwargs):
		self.request.session.flush()
		self.request.session.cycle_key()

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
		super(CreateWebsiteView, self).form_valid(form)
		self.dropbox_website = form.save()


		client = DropboxClient(self.dropbox_user.dropbox_token)
		try:
			client.metadata(self.dropbox_website.domain, file_limit=2)
			message = 'A website folder with the same name already exists in your Dropbox so we\'ve left that alone.'
		except ErrorResponse, e:
			if e.status == 404:
				output = StringIO.StringIO()
				output.write('<html>\n<head>\n  <title>Hello world</title>\n</head>\n<body>\n  <h1>Hello world...</h1>\n</body>\n</html>\n')
				try:
					client.put_file('%s/index.html' % self.dropbox_website.domain, output)
					message = 'A website folder has been created in your dropbox.'
				except Exception, e:
					logger.exception("Error creating website folder.")
					message = "An error occurred and we could not create a website folder in your dropbox. Please try creating it manually."
					logger.exception('Unexpected response from Dropbox when checking for existing folder')					
			else:
				message = "An error occurred and we could not create a website folder in your dropbox. Please try creating it manually."
				logger.exception('Unexpected response from Dropbox when checking for existing folder')

		if self.dropbox_website.domain.endswith('knownly.net'):
			message = '%s Your website is created and immediately active. <a href="%s">Check it out</a>.' % (message, self.dropbox_website.domain)
		else:
			message = '%s Your website is created although custom domains may need additional DNS configuration. <a href="%s" class="alert-link">Find out more</a>.' % (message, reverse('support'))

		return self.render_to_json_response({'domain': self.dropbox_website.domain, 'message': message})

	def form_invalid(self, form):
		return self.render_to_json_response(form.errors, status=400)

	def render_to_json_response(self, context, **response_kwargs):
		data = json.dumps(context)
		response_kwargs['content_type'] = 'application/json'
		return HttpResponse(data, **response_kwargs)

class RemoveWebsiteView(DeleteView):
	success_url = '/'
	model = DropboxSite
	http_method_names = ['post', 'put', 'delete', 'options', 'trace']

	def dispatch(self, request, *args, **kwargs):
		try:
			self.dropbox_user = DropboxUser.objects.get(pk=self.request.session['dropbox_user'])
		except DropboxUser.DoesNotExist:
			return HttpResponse('Unauthorized', status=401)

		if not request.is_ajax():
			return HttpResponseBadRequest("Only accepts XHR.")

		return super(RemoveWebsiteView, self).dispatch(request, *args, **kwargs)

	def delete(self, request, *args, **kwargs):
		try:
			dropbox_website = DropboxSite.objects.get(domain=self.request.POST['domain'])
		except DropboxSite.DoesNotExist:
			logger.exception("Attempt to delete site that doesn't exist. Domain: %s" % self.request.POST['domain'])
			context = {'message': 'Website not known at Knonwly.'}
			return self.render_to_json_response(context, status=400)
		
		if dropbox_website.dropbox_user != self.dropbox_user:
			logger.error("Attempt to delete site that doesn't belong to user making request")
			context = {'message': 'Permission denied. Our team are looking into this.'}
			return self.render_to_json_response(context, status=400)

		archived_site = ArchivedDropboxSite(dropbox_user=dropbox_website.dropbox_user, 
												domain= dropbox_website.domain, 
												date_created=dropbox_website.date_created)
		archived_site.save()
		dropbox_website.delete()

		context = {'domain': dropbox_website.domain, 
					'message': 'Website %s removed.' % dropbox_website.domain}
		return self.render_to_json_response(context, status=200)

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
