from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile  
from .models import Review,ProductQuestion
from .models import Address
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    
class ProfileForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = Profile
        fields = ['phone', 'address', 'city']

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile.save()
        return profile

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets={
            'rating':forms.NumberInput(attrs={'min':1,'max':5}),
            'comment':forms.Textarea(attrs={'rows':3}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = ProductQuestion
        fields = ['question_text']
        widgets={
            'question_text':forms.Textarea(attrs={'rows':3,'placeholder':'Ask a question..'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name','phone','pincode','address_line','city','state','address_type','is_default']
        widgets={
            'is_default':forms.CheckboxInput(attrs={'class':'form-check-input'})
            
        }