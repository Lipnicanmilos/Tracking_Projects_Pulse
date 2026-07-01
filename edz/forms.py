from django.forms import ModelForm
from .models import EDZDB
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput
from django import forms

class EDZDBUpdateForm(ModelForm):
    class Meta:
        model = EDZDB
        fields = ['EDZDB_username', 'EDZDB_password', 'EDZDB_hostname', 'EDZDB_port', 'EDZDB_servicename']
        widgets = {
            'EDZDB_username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',                
                }),
            'EDZDB_password': TextInput(attrs={
            'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
            'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
            'type': 'password',
            'id': 'BILLDB_password',
            }),
            'EDZDB_hostname': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'EDZDB_port': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'EDZDB_servicename': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
        }