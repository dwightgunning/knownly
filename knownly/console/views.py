import json
import logging
import StringIO

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
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

logger = logging.getLogger(__name__)

class IndexView(TemplateView):
	dropbox_user = None

	def get(self, request, *args, **kwargs):
		if self.request.user.is_authenticated():
			self.dropbox_user = DropboxUser.objects.get(
				django_user=request.user)

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

					logout(self.request)
					# Present a useful error to the user
					message = 'Account authentication error.'
					try:
						message = '%s %s' % (messages, e.user_error_message)
					except AttributeError, e:
						logger.exception(e)
						pass

					messages.add_message(request, messages.ERROR, message)

		return super(IndexView, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)

		if self.dropbox_user:
			context['dropbox_user'] = self.dropbox_user
			context['websites'] = DropboxSite.objects.filter(dropbox_user=self.dropbox_user)
			context['create_website_form'] = WebsiteForm({'dropboxy_user': self.dropbox_user})
			self.template_name = 'console/index.html'
		else:
			self.template_name = 'console/public.html'

		return context

class LogoutDropboxUserView(RedirectView):

	def get_redirect_url(self, **kwargs):
		logout(self.request)

		message = "Thanks for spending some time with us. Hope to see you soon!"
		messages.add_message(self.request, messages.INFO, message)
		return reverse('console')

class CreateWebsiteView(BaseFormView):
	success_url = '/'
	form_class = WebsiteForm
	http_method_names = ['post', 'put', 'options', 'trace']

	def dispatch(self, request, *args, **kwargs):
		try:
			self.dropbox_user = DropboxUser.objects.get(django_user=self.request.user)
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
					message = 'A website folder (<em>/Apps/Knownly.net/%s</em>) has been created in your Dropbox.' % self.dropbox_website.domain
				except Exception, e:
					logger.exception("Error creating website folder.")
					message = "An error occurred and we could not create a website folder in your Dropbox. Please try creating it manually."
					logger.exception('Unexpected response from Dropbox when checking for existing folder')					
			else:
				message = "An error occurred and we could not create a website folder in your Dropbox. Please try creating it manually."
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
			self.dropbox_user = DropboxUser.objects.get(django_user=self.request.user)
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
