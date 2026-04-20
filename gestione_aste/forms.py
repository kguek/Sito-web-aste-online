from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'data_nascita', 'paese', 'citta')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendiamo obbligatori nome, cognome ed email
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['data_nascita'].widget = forms.DateInput(attrs={'type': 'date'})
