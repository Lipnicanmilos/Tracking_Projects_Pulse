from django.contrib import admin
from .models import EDZDB
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class EDZDBInline(admin.StackedInline):
    model = EDZDB
    can_delete = False
    verbose_name_plural = 'Accounts'
    
    

class EDZDBCustomizeUserAdmin(UserAdmin):
    inlines = (EDZDBInline,)
    
admin.site.unregister(User)
admin.site.register(User, EDZDBCustomizeUserAdmin)

admin.site.register(EDZDB)