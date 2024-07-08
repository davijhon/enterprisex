from django.db import models
from django.urls import reverse
from django.db.models import CharField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
	#: First and last name do not cover name patterns around the globe
	name = CharField(max_length=255, blank=True)
	stripe_customer_id = CharField(max_length=50)

	def get_absolute_url(self):
		"""Get url for user's detail view.
		Returns:
			str: URL for user detail.
		"""
		return reverse("users:detail", kwargs={"username": self.username})
