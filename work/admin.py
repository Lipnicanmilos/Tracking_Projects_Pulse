from django.contrib import admin
from .models import CISDB, DWHDB, CISDB_TEST, BILLDB, EMS_DWHDB
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class CISDBInline(admin.StackedInline):
    model = CISDB
    can_delete = False
    verbose_name_plural = 'Accounts'

class BILLDBInline(admin.StackedInline):
    model = BILLDB
    can_delete = False
    verbose_name_plural = 'Accounts'

class CISDB_TEST_Inline(admin.StackedInline):
    model = CISDB_TEST
    can_delete = False
    verbose_name_plural = 'Accounts'

class DWHDBInline(admin.StackedInline):
    model = DWHDB
    can_delete = False
    verbose_name_plural = 'Accounts'

class EMSDWHDBInline(admin.StackedInline):
    model = EMS_DWHDB
    can_delete = False
    verbose_name_plural = 'Accounts'

class CISDBCustomizeUserAdmin(UserAdmin):
    inlines = (CISDBInline, DWHDBInline, CISDB_TEST_Inline, BILLDBInline, EMSDWHDBInline)


class DWHDBCustomizeUserAdmin(UserAdmin):
    inlines = (DWHDBInline, )

admin.site.unregister(User)
admin.site.register(User, CISDBCustomizeUserAdmin)
# admin.site.register(User, DWHDBCustomizeUserAdmin)

admin.site.register(CISDB)
admin.site.register(BILLDB)
admin.site.register(CISDB_TEST)
admin.site.register(DWHDB)
admin.site.register(EMS_DWHDB)


