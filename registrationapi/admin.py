from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import UserProfile, BlacklistedAccessToken

# Inline for UserProfile within User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    readonly_fields = ['profile_image_preview']

    def profile_image_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.profile_picture.url)
        return "No Image"
    profile_image_preview.short_description = "Profile Picture Preview"


# Extend UserAdmin to show UserProfile inline
class UserAdmin(DefaultUserAdmin):
    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Register the extended UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Admin for UserProfile if you want to see separately
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile_number', 'role', 'is_verified', 'is_otp_verified', 'profile_image_preview')
    readonly_fields = ['profile_image_preview']

    def profile_image_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.profile_picture.url)
        return "No Image"
    profile_image_preview.short_description = "Profile Picture"


# Admin for BlacklistedAccessToken
@admin.register(BlacklistedAccessToken)
class BlacklistedAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at')
