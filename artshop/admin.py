from django.contrib import admin
from .models import Artwork, Frame, Material, Size, CustomizedArtwork, BackgroundImage, ArtworkCategory, ArtworkCategoryImage
from django.utils.html import format_html

admin.site.register(Artwork)
admin.site.register(Frame)
admin.site.register(Material)
admin.site.register(Size)
admin.site.register(ArtworkCategory)
admin.site.register(ArtworkCategoryImage)

@admin.register(CustomizedArtwork)
class CustomizedArtworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'preview_image', 'created_at', 'is_completed')
    list_filter = ('is_completed', 'created_at')
    readonly_fields = ('preview_image', 'created_at')
    
    fieldsets = (
        (None, {
            'fields': ('preview_image', 'final_image')
        }),
        ('Status', {
            'fields': ('is_completed', 'created_at')
        }),
    )

    def preview_image(self, obj):
        if obj.final_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.final_image.url
            )
        return "-"
    preview_image.short_description = 'Preview'


@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview_image')
    readonly_fields = ('preview_image',)
    
    def preview_image(self, obj):
        return format_html('<img src="{}" style="max-height: 200px;" />', obj.image.url)
    preview_image.short_description = 'Preview'
