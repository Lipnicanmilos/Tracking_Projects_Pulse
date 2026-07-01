from django.forms import ModelForm
from .models import CISDB, DWHDB, CISDB_TEST, BILLDB, EMS_DWHDB
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput
from django import forms

class CISDBUpdateForm(ModelForm):
    class Meta:
        model = CISDB
        fields = ['CISDB_username', 'CISDB_password', 'CISDB_hostname', 'CISDB_port', 'CISDB_servicename']
        widgets = {
            'CISDB_username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',                
                }),
            'CISDB_password': TextInput(attrs={
            'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
                }),
            'CISDB_hostname': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                }),
            'CISDB_port': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                }),
            'CISDB_servicename': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                }),
        }
class BILLDBUpdateForm(ModelForm):
    show_password = forms.BooleanField(widget=forms.HiddenInput(), initial=False, required=False)

    class Meta:
        model = BILLDB
        fields = ['BILLDB_username', 'BILLDB_password', 'BILLDB_hostname', 'BILLDB_port', 'BILLDB_servicename']
        widgets = {
            'BILLDB_username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                             
                }),
            'BILLDB_password': TextInput(attrs={
            'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
            'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
            'type': 'password',
            'id': 'BILLDB_password',
            }),
            'BILLDB_hostname': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'BILLDB_port': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'BILLDB_servicename': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px; min-width: 20px;',
                }),
        }
# class BILLDBUpdateForm(ModelForm):
#     class Meta:
#         model = BILLDB
#         fields = ['BILLDB_username', 'BILLDB_password', 'BILLDB_hostname', 'BILLDB_port', 'BILLDB_servicename']
#         widgets = {
#             'BILLDB_username': TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                             
#                 }),
#             'BILLDB_password': TextInput(attrs={
#             'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
#             'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
#                 }),
                
                
#             'BILLDB_hostname': TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
#                 }),
#             'BILLDB_port': TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
#                 }),
#             'BILLDB_servicename': TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px; min-width: 20px;',
#                 }),
#         }
        


class CISDB_TEST_UpdateForm(ModelForm):
    class Meta:
        model = CISDB_TEST
        fields = ['CISDB_TEST_username', 'CISDB_TEST_password', 'CISDB_TEST_hostname', 'CISDB_TEST_port', 'CISDB_TEST_servicename']
        widgets = {
            'CISDB_TEST_username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',                
                }),
            'CISDB_TEST_password': forms.PasswordInput(),
            'CISDB_TEST_hostname': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                }),
            'CISDB_TEST_port': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                }),
            'CISDB_TEST_servicename': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                }),
        }

class DWHDBUpdateForm(ModelForm):
    class Meta:
        model = DWHDB
        fields = ['DWHDB_username', 'DWHDB_password', 'DWHDB_hostname', 'DWHDB_port', 'DWHDB_servicename']
        widgets = {
            'DWHDB_username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',                
                }),
            'DWHDB_password': TextInput(attrs={
            'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
                }),
            'DWHDB_hostname': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                }),
            'DWHDB_port': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                }),
            'DWHDB_servicename': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                }),
        }

class EMSDWHDBUpdateForm(ModelForm):
    show_password = forms.BooleanField(widget=forms.HiddenInput(), initial=False, required=False)

    class Meta:
        model = EMS_DWHDB
        fields = ['EMS_DWHDB_username', 'EMS_DWHDB_password', 'EMS_DWHDB_hostname', 'EMS_DWHDB_port', 'EMS_DWHDB_servicename']
        widgets = {
            'EMS_DWHDB_username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',                
                }),
            # 'EMS_DWHDB_password': TextInput(attrs={
            # 'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
            #     }),
            'EMS_DWHDB_password': TextInput(attrs={
            'class': "form-control text-lg h-8 rounded-full px-2 pt-1 border-2 border-black",
            'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
            'type': 'password',
            'id': 'EMS_DWHDB_password',
            }),
            'EMS_DWHDB_hostname': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'EMS_DWHDB_port': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
            'EMS_DWHDB_servicename': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; text-align: left; padding:0px; margin:0px',
                }),
        }
        
from django import forms


class DataForm(forms.Form):

    data = forms.JSONField(widget=forms.Textarea)