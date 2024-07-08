import json
from django.conf import settings
from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.views import APIView
from rest_framework.response import Response
import stripe

from .models import Pricing
from .utils import sending_info_plan

User = get_user_model()
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY



@csrf_exempt
def webhook(request):
	# You can use webhooks to receive information about asynchronous payment events.
	# For more about our webhook events check out https://stripe.com/docs/webhooks.
	webhook_secret = settings.STRIPE_WEBHOOK_SECRET
	payload = request.body

	# Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
	signature = request.META['HTTP_STRIPE_SIGNATURE']

	try:
		event = stripe.Webhook.construct_event(
			payload=payload, sig_header=signature, secret=webhook_secret
		)
		data = event['data']
	except stripe.error.SignatureVerificationError as e:
		return e
	except Exception as e:
		return e
		
	# Get the type of webhook event sent - used to check the status of PaymentIntents.
	event_type = event['type']
	data_object = data['object']

	if event_type == 'invoice.paid':
		# Used to provision services after the trial has ended.
		# The status of the invoice will show up as paid. Store the status in your
		# database to reference when a user accesses your service to avoid hitting rate
		# limits.
		# TODO: change the users subscription and pricing

		webhook_object = data["object"]
		stripe_customer_id = webhook_object["customer"]

		stripe_sub = stripe.Subscription.retrieve(webhook_object["subscription"])
		stripe_price_id = stripe_sub["plan"]["id"]

		pricing = Pricing.objects.get(stripe_price_id=stripe_price_id)

		
		user = User.objects.get(stripe_customer_id=stripe_customer_id)
		user.subscription.status = stripe_sub["status"]
		user.subscription.stripe_subscription_id = webhook_object["subscription"]
		user.subscription.pricing = pricing
		user.subscription.save()
		
		sending_info_plan(user, stripe_sub, event_type, pricing)

	if event_type == 'invoice.finalized':
		# If you want to manually send out invoices to your customers
		# or store them locally to reference to avoid hitting Stripe rate limits.
		print(data)

	if event_type == 'customer.subscription.deleted':
		# handle subscription cancelled automatically based
		# upon your subscription settings. Or if the user cancels it.
		webhook_object = data["object"]
		stripe_customer_id = webhook_object["customer"]
		stripe_sub = stripe.Subscription.retrieve(webhook_object["id"])
		user = User.objects.get(stripe_customer_id=stripe_customer_id)
		user.subscription.status = stripe_sub["status"]
		user.subscription.save()

	if event_type == 'customer.subscription.trial_will_end':
		# Send notification to your user that the trial will end
		print(data)

	if event_type == 'customer.subscription.updated':
		# if customer chance his plan, update the DB.		
		webhook_object = data["object"]
		print(webhook_object)
		stripe_customer_id = webhook_object["customer"]

		stripe_sub = stripe.Subscription.retrieve(webhook_object["id"])
		stripe_price_id = stripe_sub["plan"]["id"]

		pricing = Pricing.objects.get(stripe_price_id=stripe_price_id)

		user = User.objects.get(stripe_customer_id=stripe_customer_id)

		current_plan = user.subscription.pricing.name

		user.subscription.status = stripe_sub["status"]
		user.subscription.stripe_subscription_id = webhook_object["id"]
		user.subscription.pricing = pricing
		user.subscription.save()

		sending_info_plan(user, stripe_sub, event_type, pricing, current_plan=current_plan)

	return HttpResponse()


class PaymentView(LoginRequiredMixin, View):

	def get(self, request, slug, *args, **kwargs):
		subscription = self.request.user.subscription
		pricing = get_object_or_404(Pricing, slug=slug)

		if subscription.pricing == pricing and subscription.is_active:
			messages.info(self.request, "You are already enrolled for this package")
			return redirect("pages:pricing")

		context = {
			"pricing_tier": pricing,
			"STRIPE_PUBLIC_KEY": settings.STRIPE_TEST_PUBLIC_KEY
		}

		if subscription.is_active and subscription.pricing.stripe_price_id != "django-free-trial":
			return render(self.request, "payments/change.html", context)
	
		return render(self.request, "payments/checkout.html", context)


class CreateSubscriptionView(APIView):
	def post(self, request, *args, **kwargs):
		data = request.data
		customer_id = request.user.stripe_customer_id
		try:
			# Attach the payment method to the customer
			stripe.PaymentMethod.attach(
				data['paymentMethodId'],
				customer=customer_id,
			)
			# Set the default payment method on the customer
			stripe.Customer.modify(
				customer_id,
				invoice_settings={
					'default_payment_method': data['paymentMethodId'],
				},
			)

			# Create the subscription
			subscription = stripe.Subscription.create(
				customer=customer_id,
				items=[{'price': data["priceId"]}],
				expand=['latest_invoice.payment_intent'],
			)

			data = {}
			print('I am here')
			data.update(subscription)
			return Response(data)
		except Exception as e:
			return Response({
				"error": {'message': str(e)}
			})


class ChangeSubscriptionView(APIView):
	def post(self, request, *args, **kwargs):
		print(request.data)
		subscription_id = request.user.subscription.stripe_subscription_id
		subscription = stripe.Subscription.retrieve(subscription_id)
		try:
			updatedSubscription = stripe.Subscription.modify(
				subscription_id,
				cancel_at_period_end=False,
				items=[{
					'id': subscription['items']['data'][0].id,
					'price': request.data["priceId"],
				}],
				proration_behavior="always_invoice"
			)

			data = {}

			data.update(updatedSubscription)

			return Response(data)
		except Exception as e:
			return Response({
				"error": {'message': str(e)}
			})


class RetryInvoiceView(APIView):
	def post(self, request, *args, **kwargs):
		data = request.data
		customer_id = request.user.stripe_customer_id
		try:

			stripe.PaymentMethod.attach(
				data['paymentMethodId'],
				customer=customer_id,
			)
			# Set the default payment method on the customer
			stripe.Customer.modify(
				customer_id,
				invoice_settings={
					'default_payment_method': data['paymentMethodId'],
				},
			)

			invoice = stripe.Invoice.retrieve(
				data['invoiceId'],
				expand=['payment_intent'],
			)
			data = {}
			data.update(invoice)

			return Response(data)
		except Exception as e:

			return Response({
				"error": {'message': str(e)}
			})