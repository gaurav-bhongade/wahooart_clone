from rest_framework import serializers
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
