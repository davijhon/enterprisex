# Generated by Django 5.0.6 on 2024-07-08 20:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=50, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('button_text', models.CharField(max_length=100)),
                ('currency', models.CharField(blank=True, max_length=50, null=True)),
                ('feature', models.ManyToManyField(to='payment.feature')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('stripe_subscription_id', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=100)),
                ('pricing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='payment.pricing')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
