from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address, UserSession


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ['full_name', 'address_line_1', 'city', 'state', 'postal_code', 'country', 'is_default']


class UserSessionInline(admin.TabularInline):
    model = UserSession
    extra = 0
    readonly_fields = ['session_key', 'ip_address', 'user_agent', 'created_at', 'last_active']
    can_delete = True


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'phone', 'country', 'is_active', 'is_staff', 'is_superuser', 'email_verified', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'email_verified', 'country', 'date_joined']
    search_fields = ['email', 'username', 'phone']
    ordering = ['email']
    date_hierarchy = 'date_joined'

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'phone', 'country', 'avatar')}),
        ('Verification', {'fields': ('email_verified',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    inlines = [AddressInline, UserSessionInline]
    readonly_fields = ['date_joined', 'last_login']
    list_per_page = 12

    actions = ['activate_users', 'deactivate_users', 'verify_emails']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('addresses', 'sessions')

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} user(s) activated.')

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} user(s) deactivated.')

    @admin.action(description='Mark selected users as email verified')
    def verify_emails(self, request, queryset):
        count = queryset.update(email_verified=True)
        self.message_user(request, f'{count} user(s) marked as verified.')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'city', 'state', 'country', 'is_default', 'created_at']
    list_filter = ['is_default', 'country', 'created_at']
    search_fields = ['full_name', 'user__email', 'city', 'address_line_1']
    raw_id_fields = ['user']
    list_per_page = 12


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'ip_address', 'created_at', 'last_active']
    list_filter = ['created_at', 'last_active']
    search_fields = ['user__email', 'ip_address', 'session_key']
    raw_id_fields = ['user']
    readonly_fields = ['session_key', 'ip_address', 'user_agent', 'created_at', 'last_active']
    list_per_page = 12
