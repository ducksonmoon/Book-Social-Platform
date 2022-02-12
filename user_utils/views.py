from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

from rest_framework.views import APIView


def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "main/password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Nebig',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:

						return HttpResponse('Invalid header found.')
						
					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return HttpResponse("Password reset request sent.")
			messages.error(request, 'An invalid email has been entered.')
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="main/password/password_reset.html", context={"password_reset_form":password_reset_form})


class GoolgeAuth(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


class PasswordResetAPI(APIView):

	def post(self, request):
		email = request.data.get('email').lower()
		associated_users = User.objects.filter(Q(email=email))
		if associated_users.exists():
			for user in associated_users:
				subject = "Password Reset Requested"
				email_template_name = "main/password/password_reset_email.txt"
				c = {
				"email":user.email,
				'domain':'nebigapp.com',
				'site_name': 'Nebig',
				"uid": urlsafe_base64_encode(force_bytes(user.pk)),
				'token': default_token_generator.make_token(user),
				'protocol': 'http',
				}
				email = render_to_string(email_template_name, c)
				try:
					send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
				except BadHeaderError:
					return HttpResponse('Invalid header found.')
				messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
				return HttpResponse("Password reset request sent.")
		
		messages.error(request, 'An invalid email has been entered.')		
		return HttpResponse(status=400)
