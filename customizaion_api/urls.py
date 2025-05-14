from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import (
    SizeViewSet, FrameViewSet, MaterialViewSet, BackgroundImageViewSet, CustomizedArtworkViewSet, CategoryViewSet, ArtworkCategoryViewSet
)

router = DefaultRouter()
router.register(r'sizes', SizeViewSet)
router.register(r'frames', FrameViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'backgrounds', BackgroundImageViewSet)
router.register(r'customized-artworks', CustomizedArtworkViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'artworks-categories', ArtworkCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/upload-artwork/', views.upload_artwork, name='upload_artwork'),
    path('api/customize-artwork/', views.customize_artwork, name='customize_artwork'),
    path('api/preview-artwork/', views.preview_artwork, name='preview_artwork'),
]
