import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormView

from ipware.ip import get_ip

from knownly import plans
from knownly.billing.forms import SubscriptionPlanForm
from knownly.billing.services import CustomerBillingService
from knownly.plans.services import CustomerSubscriptionService

logger = logging.getLogger(__name__)


class PlansView(FormView):
    form_class = SubscriptionPlanForm
    template_name = 'billing/signup.html'

    PAYMENT_SUCCESS_MESSAGE = 'Thank you for your providing your credit card details. You\'ll not be charged until the end of the trial period.'
    PAYMENT_ERROR_MESSAGE = 'Unfortunately your credit card could not be authorized. Please try again.'
    FORM_INVALID_ERROR_MESSAGE = 'Unfortunately there was a problem with your details. Please try again.'

    def get_success_url(self):
        return reverse('console')

    def form_valid(self, form):
        # 3 parts to this form: the plan, billing info, and billing period
        selected_plan = form.cleaned_data['knownly_plan']
        if selected_plan != plans.FREE:
            billing_details = form.cleaned_data
            billing_details['ip_address'] = get_ip(self.request)
            
            # Update the customer's billing details
            cust_billing_service = CustomerBillingService(self.request.user)
            cust_billing_service.update_billing_details(billing_details)
            cust_billing_service.update_subscription( \
                selected_plan, billing_details['period'])

        cust_subs_service = CustomerSubscriptionService(self.request.user)
        if cust_subs_service.has_current_subscription():
            subscription = cust_subs_service.get_current_subscription()

            if subscription.current_plan != plans.FREE \
                    and selected_plan != subscription.current_plan:
                logger.exception('We haven\'t built support for changing a paid plan yet')
                raise NotImplementedError

        cust_subs_service.create_or_update_subscription( \
            plan=selected_plan, reason='Customer selected plan')

        return super(PlansView, self).form_valid(form)

    def form_invalid(self, form):
        logger.error(form.errors)
        messages.add_message(self.request, messages.ERROR, self.FORM_INVALID_ERROR_MESSAGE)
        return HttpResponseRedirect(reverse('signup'))
