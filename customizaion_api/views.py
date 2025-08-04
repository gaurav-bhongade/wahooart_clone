from django.shortcuts import render
from rest_framework import viewsets
from artshop.models import Artwork, Size, Frame, Material, CustomizedArtwork, BackgroundImage, ArtworkCategoryImage, ArtworkCategory
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import ArtworkSerializer, CustomizedArtworkSerializer
from .models import ProductCategories, Product
from .serializers import SizeSerializer, FrameSerializer, MaterialSerializer, BackgroundImageSerializer, ArtworkCategoryImageSerializer, ArtworkCategorySerializer, ArtworkSerializer, ProductCategorySerializer, ProductSerializer


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_artwork(request):
    file = request.FILES.get('image_file')
    if not file:
        return Response({"error": "No file provided"}, status=400)

    artwork = Artwork.objects.create(image_file=file, is_user_uploaded=True)
    return Response(ArtworkSerializer(artwork).data, status=201)




class ArtworkViewSet(viewsets.ModelViewSet):
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

class FrameViewSet(viewsets.ModelViewSet):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


class BackgroundImageViewSet(viewsets.ModelViewSet):
    queryset = BackgroundImage.objects.all()
    serializer_class = BackgroundImageSerializer

class CustomizedArtworkViewSet(viewsets.ModelViewSet):
    queryset = CustomizedArtwork.objects.all()
    serializer_class = CustomizedArtworkSerializer


class ArtworkCategoryViewSet(viewsets.ModelViewSet):
    queryset = ArtworkCategory.objects.all()
    serializer_class = ArtworkCategorySerializer

class ArtworkCategoryImageViewSet(viewsets.ModelViewSet):
    queryset = ArtworkCategoryImage.objects.all()
    serializer_class = ArtworkCategoryImageSerializer

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategories.objects.all()
    serializer_class = ProductCategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

