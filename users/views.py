from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, RedirectView, UpdateView, CreateView, FormView
#from django.views.generic import FormView

from .forms import CustomUserCreationForm, CancelSubscriptionForm

import stripe

User = get_user_model()
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class CancelSubscriptionView(LoginRequiredMixin, FormView):
    form_class = CancelSubscriptionForm

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def form_valid(self, form):
        stripe.Subscription.delete(self.request.user.subscription.stripe_subscription_id)
        messages.success(self.request, "You have successfully cancelled your subscription")
        return super().form_valid(form)


class UserSubscriptionView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "users/user_subscription.html"


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, ("Infos successfully updated")
        )
        return super().form_valid(form)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class SignupPageView(CreateView):
	form_class = CustomUserCreationForm
	success_url = reverse_lazy('pages:index')
	template_name = 'account/signup.html'
