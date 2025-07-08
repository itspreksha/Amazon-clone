from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
    
        if not user.has_usable_password():
            # Redirect to set password if user signed in via Google and has no password
            return reverse('set_password')
        
        # Otherwise go to homepage
        return super().get_login_redirect_url(request)
