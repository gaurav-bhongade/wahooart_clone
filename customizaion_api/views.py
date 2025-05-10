from django.shortcuts import render
from rest_framework import viewsets
from artshop.models import Artwork, Size, Frame, Material, CustomizedArtwork, BackgroundImage
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import ArtworkSerializer, CustomizedArtworkSerializer
from artshop.views import generate_customized_artwork  # your utility function

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_artwork(request):
    file = request.FILES.get('image_file')
    if not file:
        return Response({"error": "No file provided"}, status=400)

    artwork = Artwork.objects.create(image_file=file, is_user_uploaded=True)
    return Response(ArtworkSerializer(artwork).data, status=201)


def generate_customized_preview_image(artwork_id, frame_id, size_id, material_id, background_id=None):
    from io import BytesIO
    import base64
    import requests
    from PIL import Image, ImageOps, ImageFilter
    from django.shortcuts import get_object_or_404

    artwork = get_object_or_404(Artwork, id=artwork_id)
    frame = get_object_or_404(Frame, id=frame_id)
    size = get_object_or_404(Size, id=size_id)
    material = get_object_or_404(Material, id=material_id)

    art_width = int(size.width_cm * 10)
    art_height = int(size.height_cm * 10)

    if artwork.image_file:
        art_image = Image.open(artwork.image_file.path).convert('RGBA')
    else:
        response = requests.get(artwork.image_url, stream=True)
        art_image = Image.open(BytesIO(response.content)).convert('RGBA')

    art_image = art_image.resize((art_width, art_height), Image.LANCZOS)
    framed_artwork = Image.new('RGBA', (art_width, art_height), (255, 255, 255, 255))
    framed_artwork.paste(art_image, (0, 0))

    if frame.image:
        frame_img = Image.open(frame.image.path).convert('RGBA')
        frame_img = frame_img.resize((art_width, art_height), Image.LANCZOS)
        framed_artwork = Image.alpha_composite(framed_artwork, frame_img)

    if material.name.lower() == 'canvas':
        framed_artwork = ImageOps.posterize(framed_artwork, 4)
    elif material.name.lower() == 'metal':
        framed_artwork = ImageOps.autocontrast(framed_artwork)

    if background_id:
        background = get_object_or_404(BackgroundImage, id=background_id)
        bg_image = Image.open(background.image.path).convert('RGBA')
        bg_width, bg_height = bg_image.size

        art_display_width = int(bg_width * 0.15)
        scaling_factor = art_display_width / art_width
        art_display_height = int(art_height * scaling_factor)

        framed_artwork = framed_artwork.resize((art_display_width, art_display_height), Image.LANCZOS)

        x = (bg_width - art_display_width) // 2
        y = (bg_height - art_display_height) // 3

        shadow = Image.new('RGBA', (art_display_width + 20, art_display_height + 20), (0, 0, 0, 80))
        shadow_blur = shadow.filter(ImageFilter.GaussianBlur(10))

        final_image = Image.new('RGBA', (bg_width, bg_height))
        final_image.paste(bg_image, (0, 0))
        final_image.paste(framed_artwork, (x, y), framed_artwork)

        composite_image = final_image
    else:
        composite_image = framed_artwork

    img_io = BytesIO()
    composite_image.save(img_io, format='PNG')
    img_io.seek(0)
    return f'data:image/png;base64,{base64.b64encode(img_io.read()).decode()}'


@api_view(['POST'])
def customize_artwork(request):
    data = request.data
    artwork_id = data.get('artwork_id')
    size_id = data.get('size_id')
    material_id = data.get('material_id')
    frame_id = data.get('frame_id')

    try:
        artwork = get_object_or_404(Artwork, id=artwork_id)
        size = get_object_or_404(Size, id=size_id)
        material = get_object_or_404(Material, id=material_id)
        frame = get_object_or_404(Frame, id=frame_id) if frame_id else None

        customized = generate_customized_artwork(artwork, frame, size, material)

        preview_data_url = generate_customized_preview_image(
            artwork_id, frame_id, size_id, material_id
        )

        serialized_data = CustomizedArtworkSerializer(customized).data
        serialized_data['preview_image'] = preview_data_url

        return Response(serialized_data, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
def preview_artwork(request):
    from PIL import Image
    from io import BytesIO
    import base64
    import requests

    artwork_id = request.GET.get('artwork_id')
    size_id = request.GET.get('size_id')
    frame_id = request.GET.get('frame_id')

    artwork = get_object_or_404(Artwork, id=artwork_id)
    size = get_object_or_404(Size, id=size_id)
    frame = get_object_or_404(Frame, id=frame_id)

    width = int(size.width_cm * 10)
    height = int(size.height_cm * 10)

    if artwork.image_file:
        art_image = Image.open(artwork.image_file.path).convert('RGBA')
    else:
        response = requests.get(artwork.image_url, stream=True)
        art_image = Image.open(BytesIO(response.content)).convert('RGBA')

    art_image = art_image.resize((width, height), Image.LANCZOS)
    frame_image = Image.open(frame.image.path).convert('RGBA').resize((width, height), Image.LANCZOS)

    final_image = Image.alpha_composite(art_image, frame_image)
    buffer = BytesIO()
    final_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return Response({"preview_base64": image_base64})


from .serializers import SizeSerializer, FrameSerializer, MaterialSerializer, BackgroundImageSerializer

class SizeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

class FrameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer

class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class BackgroundImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BackgroundImage.objects.all()
    serializer_class = BackgroundImageSerializer