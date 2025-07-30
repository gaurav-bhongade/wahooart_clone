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


class CustomizedArtworkSerializer(serializers.ModelSerializer):
    final_image_base64 = serializers.CharField(write_only=True, required=False)
    final_image = serializers.ImageField(required=False)  # Add this line

    class Meta:
        model = CustomizedArtwork
        fields = '__all__'

    def create(self, validated_data):
        base64_image = validated_data.pop('final_image_base64', None)
        if base64_image:
            format, imgstr = base64_image.split(';base64,')
            ext = format.split('/')[-1]
            decoded_image = ContentFile(base64.b64decode(imgstr), name='custom_artwork.' + ext)
            validated_data['final_image'] = decoded_image

        return super().create(validated_data)



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
