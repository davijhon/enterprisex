from django.urls import path

from .views import (
    HomeView, 
    PricingListView, 
    AboutPageView,
    ContactView,
    Suscribir
)



app_name = 'pages'
urlpatterns = [

    path('', HomeView.as_view(), name='index'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('pricing/', PricingListView.as_view(), name='pricing'),
    path('suscribirse/' ,Suscribir.as_view(), name='suscribirse'),
    
]