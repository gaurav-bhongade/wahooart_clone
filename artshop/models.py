from django.db import models

class Artwork(models.Model):
    image_url = models.URLField(blank=True, null=True)  # Made optional
    image_file = models.ImageField(upload_to='artwork/', blank=True, null=True)  # New field for uploaded images
    is_user_uploaded = models.BooleanField(default=False)  # To distinguish user uploads from stock artwork

    def __str__(self):
        if self.image_file:
            return f"Artwork #{self.id} - {self.image_file.name}"
        return f"Artwork #{self.id} - {self.image_url or 'No image'}"

    def get_image_url(self):
        """Return the appropriate image URL, whether from file or URL field"""
        if self.image_file:
            return self.image_file.url
        return self.image_url or '' 


class Size(models.Model):
    ORIENTATION_CHOICES = [
        ('landscape', 'Landscape'),
        ('portrait', 'Portrait'),
        ('square', 'Square'),
    ]
    name = models.CharField(max_length=50)
    width_cm = models.DecimalField(max_digits=5, decimal_places=1)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1)
    orientation = models.CharField(max_length=10, choices=ORIENTATION_CHOICES)
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.width_cm}x{self.height_cm}cm)"


class Frame(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='frames/')
    price_addition = models.DecimalField(max_digits=10, decimal_places=2)
    supported_sizes = models.ManyToManyField('Size', related_name='frames')
    thickness = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='materials/')
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


from django.db import models
from django.urls import reverse

class BackgroundImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='backgrounds/')
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
class ArtworkCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class ArtworkCategoryImage(models.Model):
    category = models.ForeignKey(ArtworkCategory, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ImageField(upload_to='artworkcategory/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    supported_sizes = models.ManyToManyField('Size', related_name='category_images', blank=True)
    is_user_uploaded = models.BooleanField(default=False)
    def __str__(self):
        if self.image_file:
            return f"Artwork Category # {self.category.name} - {self.id} - {self.image_file.name}"
        return f"Artwork Category # {self.category.name} - {self.id} - {self.image_url or 'No image'}"

class CustomizedArtwork(models.Model):
    artwork = models.ImageField(upload_to='customized_artwork/')
    selected_frame = models.ForeignKey(Frame, on_delete=models.SET_NULL, null=True) 
    final_image = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Custom Art #{self.id}"

    def get_absolute_url(self):
        return reverse('admin:artshop_customizedartwork_change', args=[self.id])


