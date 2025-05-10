from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'artshop'

urlpatterns = [
    path('', views.index, name='index'),
    path('custom-art/', views.custom_art, name='custom_art'),
    path('api/calculate_price/', views.calculate_price, name='calculate_price'),
    path('generate-preview/', views.generate_preview, name='generate_preview'),
    path('custom-art-preview/<int:customized_id>/', views.custom_art_preview, name='custom_art_preview'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
