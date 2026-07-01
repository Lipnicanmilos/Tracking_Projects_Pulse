from django.db import models
from project.settings import DATABASES
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField

# Create your models here.
class EETSDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    EETSDB_username = models.CharField(max_length=30, default="Name_Surname")
    EETSDB_password = EncryptedCharField(max_length=100, default="YourPassword#01")
    EETSDB_hostname = models.CharField(max_length=30, default="oradb-a01.infra.internal.example.com")
    EETSDB_port = models.CharField(max_length=30, default="1521")
    EETSDB_servicename = models.CharField(max_length=30, default="primary_bill.infra.internal.example.com")

    def __str__(self):
        return self.user.username
    
class SAIDAMDDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    SAIDAMD_username = models.CharField(max_length=30, default="Name_Surname")
    SAIDAMD_password = EncryptedCharField(max_length=100, default="YourPassword#01")
    SAIDAMD_hostname = models.CharField(max_length=30, default="oradb-a01.infra.internal.example.com")
    SAIDAMD_port = models.CharField(max_length=30, default="1521")
    SAIDAMD_servicename = models.CharField(max_length=30, default="primary_md.infra.internal.example.com")

    def __str__(self):
        return self.user.username
    
class PROXYDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    PROXYDB_username = models.CharField(max_length=30, default="Name_Surname")
    PROXYDB_password = EncryptedCharField(max_length=100, default="YourPassword#01")
    PROXYDB_hostname = models.CharField(max_length=30, default="oradb-a01.infra.internal.example.com")
    PROXYDB_port = models.CharField(max_length=30, default="1521")
    PROXYDB_servicename = models.CharField(max_length=40, default="primary_proxy.infra.internal.example.com")

    def __str__(self):
        return self.user.username