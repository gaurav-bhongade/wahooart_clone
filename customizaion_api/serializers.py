from rest_framework import serializers
import base64
import uuid
from django.core.files.base import ContentFile
from artshop.models import Artwork, Size, Frame, Material, CustomizedArtwork, BackgroundImage, ArtworkCategoryImage, ArtworkCategory
from . models import Product, ProductCategories


class ArtworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artwork
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'

class FrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frame
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class BackgroundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackgroundImage
        fields = '__all__'

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # Decode the base64 image
            format, imgstr = data.split(';base64,')  # format ~= data:image/X
            ext = format.split('/')[-1]  # guess file extension
            id = uuid.uuid4().hex[:10]
            data = ContentFile(base64.b64decode(imgstr), name=f"{id}.{ext}")
        return super().to_internal_value(data)

class CustomizedArtworkSerializer(serializers.ModelSerializer):
    final_image = Base64ImageField()

    class Meta:
        model = CustomizedArtwork
        fields = '__all__'

class ArtworkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtworkCategory
        fields = '__all__'

class ArtworkCategoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtworkCategoryImage
        fields = '__all__'

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategories
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
