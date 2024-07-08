from django.contrib import admin

from .models import Pricing, Subscription, Feature


admin.site.register(Feature)
admin.site.register(Pricing)
admin.site.register(Subscription)
