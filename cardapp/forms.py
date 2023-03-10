from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import CardData
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm



# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise ValidationError("Email already exists")
		return email
		
	# def save(self, commit=True):
	# 	user = super(NewUserForm, self).save(commit=False)
	# 	user.email = self.cleaned_data['email']
	# 	if commit:
	# 		user.save()
	# 	return user


# class CardForm(forms.ModelForm):
#    class Meta:
#       model=CardData
#       #fields="__all__"
#       fields=('firstname','middlename','lastname','title','department','company','phone','upload','email')

	  
class sendForm(forms.Form):
	email=forms.EmailField(label="Enter email",max_length=50)
	class Meta:
		model=CardData
		fields="__all__"


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'input-field',
            'placeholder': 'Enter your email',
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'New Password',
        })
    )
    new_password2 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Confirm Password',
        })
    )