import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView
from ipware.ip import get_ip

from knownly import plans
from knownly.billing.errors import PaymentProviderError
from knownly.billing.forms import SubscriptionPlanForm
from knownly.billing.services import CustomerBillingService
from knownly.plans.services import CustomerSubscriptionService

logger = logging.getLogger(__name__)


class PlansView(FormView):
    form_class = SubscriptionPlanForm
    template_name = 'billing/plans.html'
    mode = 'plans'

    FREE_PLAN_SUCCSS_MESSAGE = 'Thanks for joining Knownly!'
    PAYMENT_SUCCESS_MESSAGE = 'Thanks for joining Knownly!'

    def get_success_url(self):
        return reverse('console')

    def get_context_data(self, **kwargs):
        context_data = super(PlansView, self).get_context_data(**kwargs)
        context_data['mode'] = self.mode

        return context_data

    def form_valid(self, form):
        # 3 parts to this form: the plan, billing info, and billing period
        selected_plan = form.cleaned_data['knownly_plan']
        if selected_plan in [plans.LITE, plans.PREMIUM]:
            billing_details = form.cleaned_data
            billing_details['ip_address'] = get_ip(self.request)

            # Update the customer's billing details
            try:
                cust_billing_service = \
                    CustomerBillingService(self.request.user)
                cust_billing_service.update_billing_details(billing_details)
                cust_billing_service.update_subscription(
                    selected_plan, billing_details['period'])
            except PaymentProviderError:
                logger.exception('Payment Provider error encountered '
                                 'while creating customer: %s',
                                 self.request.user)
                form.add_error('__all__',
                               ValidationError('There was a problem '
                                               'problem validating your '
                                               'credit card.'))
                return super(PlansView, self).form_invalid(form)
            except Exception:
                logger.exception('Payment Provider error encountered while '
                                 'creating customer: %s', self.request.user)
                form.add_error('__all__',
                               ValidationError('There was a problem updating '
                                               'your subscription. We will '
                                               'look into it and be in '
                                               'contact with you.'))
                return super(PlansView, self).form_invalid(form)

        cust_subs_service = CustomerSubscriptionService(self.request.user)
        if cust_subs_service.has_current_subscription():
            subscription = cust_subs_service.get_current_subscription()

            if subscription.current_plan != plans.FREE \
                    and selected_plan != subscription.current_plan:
                logger.exception('We haven\'t built support for changing a '
                                 'paid plan yet. Attempted by %s',
                                 self.request.user)
                form.add_error('__all__',
                               ValidationError('Please contact us '
                                               '(info@knownly.net) to arrange '
                                               'a change in your plan.'))
                return super(PlansView, self).form_invalid(form)

        try:
            cust_subs_service.create_or_update_subscription(
                plan=selected_plan, reason='Customer selected plan')
            if selected_plan == plans.FREE:
                messages.add_message(self.request, messages.SUCCESS,
                                     self.FREE_PLAN_SUCCSS_MESSAGE)
            else:
                messages.add_message(self.request, messages.SUCCESS,
                                     self.PAYMENT_SUCCESS_MESSAGE)
        except PaymentProviderError:
            logger.exception('Payment Provider error encountered while '
                             'updating subscription for customer: %s',
                             self.request.user)
            form.add_error('__all__',
                           ValidationError('There was a problem updating your '
                                           'subscription. We will look into '
                                           'it and be in contact with you.'))
            return super(PlansView, self).form_invalid(form)
        except Exception:
            logger.exception('Payment Provider error encountered while '
                             'updating subscription for customer: %s',
                             self.request.user)
            form.add_error('__all__',
                           ValidationError('There was a problem updating your '
                                           'subscription. We will look into '
                                           'it and be in contact with you.'))
            return super(PlansView, self).form_invalid(form)

        return super(PlansView, self).form_valid(form)

    def form_invalid(self, form):
        logger.debug(form.errors)
        return super(PlansView, self).form_invalid(form)
