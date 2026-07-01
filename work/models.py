from django.db import models
from project.settings import DATABASES
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField


class CISDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    CISDB_username = models.CharField(max_length=30, default="Name_Surname")
    CISDB_password = EncryptedCharField(max_length=100, default="YourPassword#01")
    CISDB_hostname = models.CharField(max_length=30, default="db-host-b.internal.example.com")
    CISDB_port = models.CharField(max_length=30, default="1521")
    CISDB_servicename = models.CharField(max_length=30, default="cissrv_rdo")

    def __str__(self):
        return self.user.username

class CISDB_TEST(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    CISDB_TEST_username = models.CharField(max_length=30, default="Name_Surname")
    CISDB_TEST_password = EncryptedCharField(max_length=100)
    
    CISDB_TEST_hostname = models.CharField(max_length=30, default="db-host-b.internal.example.com")
    CISDB_TEST_port = models.CharField(max_length=30, default="1521")
    CISDB_TEST_servicename = models.CharField(max_length=30, default="cissrv_rdo")

    def __str__(self):
        return self.user.username
    
class EMS_DWHDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    EMS_DWHDB_username = models.CharField(max_length=30, default="Name")
    EMS_DWHDB_password = EncryptedCharField(max_length=100, default="YourPassword#01")
    EMS_DWHDB_hostname = models.CharField(max_length=30, default="scan-dwh.etc.example")
    EMS_DWHDB_port = models.CharField(max_length=30, default="1521")
    EMS_DWHDB_servicename = models.CharField(max_length=30, default="dwh")

    def __str__(self):
        return self.user.username

class DWHDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    DWHDB_username = models.CharField(max_length=30, default="Name_Surname")
    DWHDB_password = EncryptedCharField(max_length=100, default="YourPassword#01")
    DWHDB_hostname = models.CharField(max_length=30, default="ADB01.internal.example.com")
    DWHDB_port = models.CharField(max_length=30, default="1539")
    DWHDB_servicename = models.CharField(max_length=30, default="dwh")

    def __str__(self):
        return self.user.username
    
class BILLDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    BILLDB_username = models.CharField(max_length=30, default="username")
    BILLDB_password = EncryptedCharField(max_length=100, default="YourPassword#01")
    BILLDB_hostname = models.CharField(max_length=30, default="scan-billdb.etc.example")
    BILLDB_port = models.CharField(max_length=30, default="1521")
    BILLDB_servicename = models.CharField(max_length=30, default="billdb.etc.example.sk")

    def __str__(self):
        return self.user.username
    
# class CisAcAdUser(models.Model):
#     ad_user_id = models.CharField(db_column='AD_USER_ID', primary_key=True, max_length=10)  # Field name made lowercase.
#     username = models.CharField(db_column='USERNAME', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     secure_id = models.CharField(db_column='SECURE_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     ad_creation_date = models.CharField(db_column='AD_CREATION_DATE', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     delete_on = models.DateTimeField(db_column='DELETED_ON', max_length=50, blank=True, null=True)
#     class Meta:
#         managed = False
#         db_table = 'CIS_AC\".\"AD_USER'
#         app_label = 'cis_db'

# class CisUserDetail(models.Model):
#     user_id = models.CharField(db_column='USER_ID', primary_key=True, max_length=10)  # Field name made lowercase.
#     username = models.CharField(db_column='USER_NAME', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     secure_id = models.CharField(db_column='SECURE_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     selfcare_user_group_id = models.CharField(db_column='SELFCARE_USER_GROUP_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     creation_date = models.DateTimeField(db_column='CREATION_DATETIME', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     expiration_date = models.DateTimeField(db_column='EXPIRATION_DATE', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     delete_on = models.DateTimeField(db_column='DELETED_ON', max_length=50, blank=True, null=True)  # Field name made lowercase.
    
#     class Meta:
#         managed = False
#         db_table = 'CIS_AC\".\"USER_DETAIL'
#         app_label = 'cis_db'

class CIS_SCHEDULED_JOB(models.Model):
    job_id = models.CharField(db_column='SCHEDULED_JOB_ID', primary_key=True, max_length=10)  # Field name made lowercase.
    job_name = models.CharField(db_column='JOB_NAME', max_length=50, blank=True, null=True)  # Field name made lowercase.
    job_description = models.CharField(db_column='JOB_DESCRIPTION', max_length=50, blank=True, null=True)  # Field name made lowercase.
    change_on = models.DateTimeField(db_column='CHANGED_ON', max_length=50, blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        managed = False
        db_table = 'CIS_CO\".\"SCHEDULED_JOB'
        app_label = 'cis_db'

class JOB_INSTANCE(models.Model):
    job_id = models.CharField(db_column='SCHEDULED_JOB_ID', primary_key=True, max_length=10)  # Field name made lowercase.
    action_datetime = models.DateTimeField(db_column='ACTION_DATETIME', max_length=50, blank=True, null=True)  # Field name made lowercase.
    state_code = models.CharField(db_column='EXECUTION_STATE_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    expected_n_of_items = models.CharField(db_column='EXPECTED_NUMBER_OF_ITEMS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    successfully_processed_items = models.CharField(db_column='SUCCESSFULLY_PROCESSED_ITEMS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        managed = False
        db_table = 'CIS_CO\".\"JOB_INSTANCE'
        app_label = 'cis_db'

class EXECUTION_L(models.Model):
    EXECUTION_STATE_CODE = models.CharField(db_column='EXECUTION_STATE_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    LANGUAGE_CODE = models.CharField(db_column='LANGUAGE_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    EXECUTION_STATE_NAME = models.CharField(db_column='EXECUTION_STATE_NAME', max_length=50, blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        managed = False
        db_table = 'CIS_CO\".\"EXECUTION_STATE_L'
        app_label = 'cis_db'