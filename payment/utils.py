from datetime import datetime
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import send_mail



def sending_info_plan(user, sub, event, plan, current_plan=''):
	# This function send a email to a customer
	# with the info about the plan changed or buyed
	# try:
	trial_start = datetime.utcfromtimestamp(sub['trial_start']).strftime('%b. %d, %Y')
	trial_end = datetime.utcfromtimestamp(sub['trial_end']).strftime('%b. %d, %Y')
	trial_period_days = sub['plan']['trial_period_days']


	subject = 'Test Order Email'
	html_message = render_to_string('payments/email/email_plan_info.html', {'plan': plan, 
										  						  				'event': event,
																  				'trial_end': trial_end,	
																  				'trial_start': trial_start,
																  				'current_plan': current_plan,
																  				'trial_period_days': trial_period_days,})
	plain_message = strip_tags(html_message)
	from_email = settings.DEFAULT_FROM_EMAIL
	to = user.email

	send_mail(subject, plain_message, from_email, [to], html_message=html_message)
	# except:
	# 	print('Message not sended')