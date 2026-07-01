from django.db import models
from project.settings import DATABASES
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField

# Create your models here.
class EDZDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    EDZDB_username = models.CharField(max_length=30, default="Name_Surname")
    EDZDB_password = EncryptedCharField(max_length=100, default="YourPassword#01")
    EDZDB_hostname = models.CharField(max_length=30, default="oradb-a01.infra.eznamka.sk")
    EDZDB_port = models.CharField(max_length=30, default="1521")
    EDZDB_servicename = models.CharField(max_length=30, default="primary_edz")

    def __str__(self):
        return self.user.username