
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
from decimal import Decimal
from .forms import CustomerForm, ArtworkCustomizationForm
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Artwork, Frame, Size, Material, CustomizedArtwork, BackgroundImage
from PIL import Image, ImageOps, ImageFilter
import base64
from django.contrib import messages

def index(request):
    """Home page view"""
    return redirect('artshop:custom_art')


@csrf_exempt
def calculate_price(request):
    """API endpoint to calculate price based on selections"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get selected options
            artwork_id = data.get('artwork_id')
            size_id = data.get('size_id')
            frame_id = data.get('frame_id')
            material_id = data.get('material_id')
            
            # Retrieve objects
            artwork = Artwork.objects.get(id=artwork_id)
            size = Size.objects.get(id=size_id)
            frame = Frame.objects.get(id=frame_id)
            material = Material.objects.get(id=material_id)
            
            # Calculate price
            base_price = artwork.base_price
            size_adjusted_price = base_price * size.price_multiplier
            frame_price = frame.price_addition
            material_adjusted_price = size_adjusted_price * material.price_multiplier
            
            total_price = material_adjusted_price + frame_price
            
            return JsonResponse({
                'base_price': float(base_price),
                'size_adjusted_price': float(size_adjusted_price),
                'frame_price': float(frame_price),
                'material_adjusted_price': float(material_adjusted_price),
                'total_price': float(total_price)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def generate_customized_artwork(artwork, frame, size, material, background=None):
    # Open images
    art_image = Image.open(artwork.image_file.path).convert("RGBA")
    frame_image = Image.open(frame.image.path).convert("RGBA")

    # Calculate dimensions
    new_width = int(size.width_cm * 10)
    new_height = int(size.height_cm * 10)

    # Resize images
    resized_art = art_image.resize((new_width, new_height), Image.LANCZOS)
    resized_frame = frame_image.resize((new_width, new_height), Image.LANCZOS)

    # Composite artwork with frame
    final_image = Image.alpha_composite(resized_art, resized_frame)

    if frame:
        # If frame is selected, composite with frame
        frame_image = Image.open(frame.image.path).convert("RGBA")
        resized_frame = frame_image.resize((new_width, new_height), Image.LANCZOS)
        final_image = Image.alpha_composite(resized_art, resized_frame)
    else:
        # If no frame selected, use artwork as-is
        final_image = resized_art

    # If background is provided, composite it with the artwork
    if background:
        bg_image = Image.open(background.image.path).convert("RGBA")
        bg_width = int(new_width * 1.5)
        bg_height = int(new_height * 1.5)
        bg_image = bg_image.resize((bg_width, bg_height), Image.LANCZOS)
        
        # Position the artwork in the center of the background
        x = (bg_width - new_width) // 2
        y = (bg_height - new_height) // 2
        
        # Create new image with background dimensions
        bg_composite = Image.new('RGBA', (bg_width, bg_height))
        bg_composite.paste(bg_image, (0, 0))
        bg_composite.paste(final_image, (x, y), final_image)
        final_image = bg_composite

    # Save to buffer
    buffer = BytesIO()
    final_image.save(buffer, format='PNG')
    file_name = f"custom_art_{artwork.id}_{frame.id}_{size.id}_{material.id}.png"
    
    # Create and save the customized artwork
    customized = CustomizedArtwork.objects.create(
        original_artwork=artwork,
        selected_frame=frame,
        selected_size=size,
        selected_material=material,
        selected_background=background,
        final_image=ContentFile(buffer.getvalue(), name=file_name)
    )
    
    return customized


def custom_art(request):
    if request.method == 'POST':
        if 'custom_artwork' in request.FILES:
            # Handle image upload
            custom_image = request.FILES['custom_artwork']
            artwork = Artwork.objects.create(
                image_file=custom_image,
                is_user_uploaded=True
            )
            return redirect(reverse('artshop:custom_art') + f'?artwork_id={artwork.id}')

        elif 'confirm_customization' in request.POST:
            try:
                # Handle customization confirmation
                artwork_id = request.POST.get('artwork_id')
                frame_id = request.POST.get('frame')
                size_id = request.POST.get('size')
                material_id = request.POST.get('material')
                
                if not all([artwork_id, size_id, material_id]):
                    raise ValueError("Missing required fields")
                
                artwork = get_object_or_404(Artwork, id=artwork_id)
                size = get_object_or_404(Size, id=size_id)
                material = get_object_or_404(Material, id=material_id)
                
                # Handle optional frame
                frame = None
                if frame_id:  # Only get frame if frame_id is not empty
                    frame = get_object_or_404(Frame, id=frame_id)

                # Create the customized artwork
                customized = generate_customized_artwork(artwork, frame, size, material)
                
                # Add customer info if available
                customer_form = CustomerForm(request.POST)
                if customer_form.is_valid():
                    customized.customer_name = customer_form.cleaned_data['name']
                    customized.customer_email = customer_form.cleaned_data['email']
                    customized.save()
                
                messages.success(request, 'Your artwork has been customized successfully!')
                return redirect('artshop:custom_art_preview', customized_id=customized.id)
            
            except ValueError as e:
                messages.error(request, str(e))
                return redirect(reverse('artshop:custom_art') + f'?artwork_id={request.POST.get("artwork_id")}')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect(reverse('artshop:custom_art'))

    artwork_id = request.GET.get('artwork_id')
    artwork = Artwork.objects.filter(id=artwork_id).first() if artwork_id else None

    sizes = Size.objects.all()
    frames = Frame.objects.all()
    backgrounds = BackgroundImage.objects.all()
    materials = Material.objects.all()
    customer_form = CustomerForm()
    customization_form = ArtworkCustomizationForm()
    featured_artworks = Artwork.objects.filter(is_user_uploaded=False)

    context = {
        'artwork': artwork,
        'sizes': sizes,
        'frames': frames,
        'materials': materials,
        'customer_form': customer_form,
        'customization_form': customization_form,
        'featured_artworks': featured_artworks,
        'backgrounds': backgrounds,
    }
    return render(request, 'artshop/custom_art2.html', context)


def generate_preview(request):
    artwork_id = request.GET.get('artwork_id')
    frame_id = request.GET.get('frame_id')
    size_id = request.GET.get('size_id')
    material_id = request.GET.get('material_id')
    background_id = request.GET.get('background_id', None)

    artwork = get_object_or_404(Artwork, id=artwork_id)
    frame = get_object_or_404(Frame, id=frame_id)
    size = get_object_or_404(Size, id=size_id)
    material = get_object_or_404(Material, id=material_id)

    # Calculate artwork dimensions in pixels (assuming 10 pixels per cm)
    art_width = int(size.width_cm * 10)
    art_height = int(size.height_cm * 10)

    # Open artwork image
    if artwork.image_file:
        art_image = Image.open(artwork.image_file.path).convert('RGBA')
    else:
        # Handle URL case
        import requests
        response = requests.get(artwork.image_url, stream=True)
        art_image = Image.open(BytesIO(response.content)).convert('RGBA')

    # Resize artwork to selected size
    art_image = art_image.resize((art_width, art_height), Image.LANCZOS)

    # Create a new image with the frame dimensions
    framed_artwork = Image.new('RGBA', (art_width, art_height), (255, 255, 255, 255))
    
    # Paste the artwork (will fill the entire frame)
    framed_artwork.paste(art_image, (0, 0))

    # Apply frame if available (must be PNG with transparency)
    if frame.image:
        frame_img = Image.open(frame.image.path).convert('RGBA')
        frame_img = frame_img.resize((art_width, art_height), Image.LANCZOS)
        
        # Composite the frame over the artwork (frame must have transparency)
        framed_artwork = Image.alpha_composite(framed_artwork, frame_img)

    # Apply material effects
    if material.name.lower() == 'canvas':
        framed_artwork = ImageOps.posterize(framed_artwork, 4)
    elif material.name.lower() == 'metal':
        framed_artwork = ImageOps.autocontrast(framed_artwork)

    # If background is selected
    if background_id:
        background = get_object_or_404(BackgroundImage, id=background_id)
        bg_image = Image.open(background.image.path).convert('RGBA')
        
        # Keep background at original size
        bg_width, bg_height = bg_image.size
        
        # Calculate artwork size to be about 25% of background width (smaller than before)
        art_display_width = int(bg_width * 0.15)  # Reduced from 0.35 to 0.25
        scaling_factor = art_display_width / art_width
        art_display_height = int(art_height * scaling_factor)
        
        # Resize the framed artwork to fit within background
        framed_artwork = framed_artwork.resize((art_display_width, art_display_height), Image.LANCZOS)
        
        # Calculate position - centered horizontally and slightly below center vertically
        x = (bg_width - art_display_width) // 2  # Centered horizontally
        y = (bg_height - art_display_height) // 3  # 1/3 from top (slightly below center)
        
        # Create shadow effect
        shadow = Image.new('RGBA', (art_display_width + 20, art_display_height + 20), (0, 0, 0, 80))
        shadow_blur = shadow.filter(ImageFilter.GaussianBlur(10))
        
        # Create final image
        final_image = Image.new('RGBA', (bg_width, bg_height))
        final_image.paste(bg_image, (0, 0))

        final_image.paste(framed_artwork, (x, y), framed_artwork)
        composite_image = final_image
    else:
        composite_image = framed_artwork

    # Convert to base64 for web preview
    img_io = BytesIO()
    composite_image.save(img_io, format='PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.read()).decode()

    return JsonResponse({'image_url': f'data:image/png;base64,{img_base64}'})




def custom_art_preview(request, customized_id):
    customized = get_object_or_404(CustomizedArtwork, id=customized_id)
    context = {
        'customized': customized,
        'admin_url': customized.get_absolute_url()
    }
    return render(request, 'artshop/custom_art_preview.html', context)