import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormView

from knownly.billing.forms import SubscriptionPlanForm
from knownly.billing.services import StripeCustomerService

logger = logging.getLogger(__name__)

class PaidPlanRegistrationView(FormView):
    http_method_names = ['post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    form_class = SubscriptionPlanForm

    PAYMENT_SUCCESS_MESSAGE = "Thankyou for your providing your credit card details. You'll not be charged until the end of your trial period."
    PAYMENT_ERROR_MESSAGE = "Unfortunately your credit card could not be authorized. Please try again."
    FORM_INVALID_ERROR_MESSAGE = "Unfortunately there was a problem with your details. Please try again."

    def get_success_url(self):
        return reverse('index')

    def form_valid(self, form):
    	if form.cleaned_data['email'] != self.request.user.email:
    		self.request.user.email = form.cleaned_data['email']
    		self.request.user.save()

    	if form.cleaned_data['plan'] != 'free':
	        stripe_payment_service = StripePaymentService()
	        stripe_payment_service.create_stripe_customer(self.request.user, form.cleaned_data['stripeToken'])


        return super(PaidPlanRegistrationView, self).form_valid(form)

    def form_invalid(self, form):
        logger.error(form.errors)
        messages.add_message(self.request, messages.ERROR, self.FORM_INVALID_ERROR_MESSAGE)
        return HttpResponseRedirect(reverse('signup'))
