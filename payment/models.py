from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.signals import user_logged_in
from django.utils.text import slugify
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from allauth.account.signals import email_confirmed
import stripe

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

User = get_user_model()


class Feature(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Pricing(models.Model):
    name = models.CharField(max_length=100)  # Free / Basic / Premium
    slug = models.SlugField(unique=True)
    stripe_price_id = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    feature = models.ManyToManyField(Feature)
    button_text = models.CharField(max_length=100)
    currency = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pricing = models.ForeignKey(
        Pricing, on_delete=models.CASCADE, related_name="subscriptions"
    )
    created = models.DateTimeField(auto_now_add=True)
    stripe_subscription_id = models.CharField(max_length=50)
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.user.email

    @property
    def is_active(self):
        return self.status == "active" or self.status == "trialing"


def post_email_confirmed(request, email_address, *args, **kwargs):
    user = User.objects.get(email=email_address.email)
    free_trial_pricing = Pricing.objects.get(name="Free Plan")
    subscription = Subscription.objects.create(user=user, pricing=free_trial_pricing)
    stripe_customer = stripe.Customer.create(email=user.email)
    stripe_subscription = stripe.Subscription.create(
        customer=stripe_customer["id"],
        items=[{"price": "price_1HTFm8JQrBxwDnChUzQRKkrb"}],
        trial_period_days=7,
    )
    subscription.status = stripe_subscription["status"]  # trialing
    subscription.stripe_subscription_id = stripe_subscription["id"]
    subscription.save()
    user.stripe_customer_id = stripe_customer["id"]
    user.save()


def user_logged_in_receiver(sender, user, **kwargs):
    if not user.is_superuser:
        subscription = user.subscription
        sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)

        subscription.status = sub["status"]
        subscription.save()


user_logged_in.connect(user_logged_in_receiver)
email_confirmed.connect(post_email_confirmed)
