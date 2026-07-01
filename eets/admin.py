from django.contrib import admin
from .models import EETSDB, SAIDAMDDB, PROXYDB
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class EETSDBInline(admin.StackedInline):
    model = EETSDB
    can_delete = False
    verbose_name_plural = 'Accounts'
    
class SAIDAMDDBInline(admin.StackedInline):
    model = SAIDAMDDB
    can_delete = False
    verbose_name_plural = 'Accounts'    

class PROXYDBInline(admin.StackedInline):
    model = PROXYDB
    can_delete = False
    verbose_name_plural = 'Accounts' 

class EETSDBCustomizeUserAdmin(UserAdmin):
    inlines = (EETSDBInline, SAIDAMDDBInline, PROXYDBInline,)


admin.site.unregister(User)
admin.site.register(User, EETSDBCustomizeUserAdmin)
admin.site.register(EETSDB)
admin.site.register(SAIDAMDDB)
admin.site.register(PROXYDB)
