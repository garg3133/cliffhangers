from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from .forms import UserAdminCreationForm

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances

    # form = UserAdminChangeForm
    # Will override default password checks (like password too common)
    # and validations with those specified in this form.
    # Also 'role' and other field won't work without this.
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'get_full_name', 'role', 'is_active', 'auth')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'auth', 'is_active', 'is_staff')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role', 'contact_no')}),
        ('Permissions', {'fields': ('is_active', 'auth', 'is_staff', 'is_superuser')}),
        ('Permissions and Groups', {'fields': ('user_permissions', 'groups')}),
        ('Others', {'fields': ('date_joined', 'last_login')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ('user_permissions', 'groups')

    def get_full_name(self, obj):
        return f'{obj.get_full_name}'
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'first_name'