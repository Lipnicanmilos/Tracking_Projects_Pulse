from django.forms import ModelForm
from .models import EETSDB, SAIDAMDDB, PROXYDB
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput
from django import forms

class EETSDBUpdateForm(ModelForm):
    class Meta:
        model = EETSDB
        fields = ['EETSDB_username', 'EETSDB_password', 'EETSDB_hostname', 'EETSDB_port', 'EETSDB_servicename']
        widgets = {
            'EETSDB_username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',                
                }),
            'EETSDB_password': TextInput(attrs={
            'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
            'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
            'type': 'password',
            'id': 'BILLDB_password',
            }),
            'EETSDB_hostname': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'EETSDB_port': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'EETSDB_servicename': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
        }

class SAIDAMDDBUpdateForm(ModelForm):
    class Meta:
        model = SAIDAMDDB
        fields = ['SAIDAMD_username', 'SAIDAMD_password', 'SAIDAMD_hostname', 'SAIDAMD_port', 'SAIDAMD_servicename']
        widgets = {
            'SAIDAMD_username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',                
                }),
            'SAIDAMD_password': TextInput(attrs={
            'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
            'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
            'type': 'password',
            'id': 'SAIDAMD_password',
            }),
            'SAIDAMD_hostname': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'SAIDAMD_port': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'SAIDAMD_servicename': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
        }

class PROXYDBUpdateForm(ModelForm):
    class Meta:
        model = PROXYDB
        fields = ['PROXYDB_username', 'PROXYDB_password', 'PROXYDB_hostname', 'PROXYDB_port', 'PROXYDB_servicename']
        widgets = {
            'PROXYDB_username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',                
                }),
            'PROXYDB_password': TextInput(attrs={
            'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
            'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
            'type': 'password',
            'id': 'PROXYDB_password',
            }),
            'PROXYDB_hostname': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'PROXYDB_port': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'PROXYDB_servicename': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
        }