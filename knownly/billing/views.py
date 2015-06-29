import json
import logging
import stripe

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from knownly.billing.services import StripeEventHandler

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@require_POST
@csrf_exempt
def stripe_webhook(request):
    try:
        # Retrieve the request's body and parse it as JSON
        event_json = json.loads(request.body)
        event_id = event_json['id']

        event_handler = StripeEventHandler()
        event_handler.handle_event(event_id)
    except:
        logger.exception("Error handling Stripe event.")

    return HttpResponse(status=200)
