from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import (
    SizeViewSet, FrameViewSet, MaterialViewSet, BackgroundImageViewSet, CustomizedArtworkViewSet, ArtworkCategoryImageViewSet, ArtworkCategoryViewSet, ArtworkViewSet, ProductCategoryViewSet, ProductViewSet
)

router = DefaultRouter()
router.register(r'artworks', ArtworkViewSet)
router.register(r'sizes', SizeViewSet)
router.register(r'frames', FrameViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'backgrounds', BackgroundImageViewSet)
router.register(r'customized-artworks', CustomizedArtworkViewSet)
router.register(r'artwork-categories', ArtworkCategoryViewSet)
router.register(r'artworks-categories-image', ArtworkCategoryImageViewSet)
router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/upload-artwork/', views.upload_artwork, name='upload_artwork'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
