from django.urls import path 

from .views import (
	PaymentView, 
	CreateSubscriptionView, 
	ChangeSubscriptionView,
	RetryInvoiceView,
	webhook
)


app_name = 'payments'
urlpatterns = [

	path('plan/<slug>/', PaymentView.as_view(), name='checkout'),
	path('create-subscription/', CreateSubscriptionView.as_view(), name='create-subscription'),
	path('change-subscription/', ChangeSubscriptionView.as_view(), name='change-subscription'),
	path('retry-invoice/', RetryInvoiceView.as_view(), name='retry-invoice'),
	path('webhook/', webhook, name='webhook'),

]