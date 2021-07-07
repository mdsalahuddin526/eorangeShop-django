from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import Account


class AccountAdmin(BaseUserAdmin):
    list_display =('email', 'first_name', 'last_name', 'username', 'date_joined', 'last_login', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login',)
    ordering = ('-date_joined',)

    list_filter = ()
    fieldsets = ()        
    search_fields = ('email',)    
    filter_horizontal = ()

admin.site.register(Account, AccountAdmin)



