from django.db import models
import os

class ProductCategories(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
def product_image_upload_to(instance, filename):
    product_name = instance.name.replace(" ", "_")  # Optional: sanitize name
    return os.path.join('products', product_name, filename)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to=product_image_upload_to)
    image1 = models.ImageField(blank=True, null=True, upload_to=product_image_upload_to)
    image2 = models.ImageField(blank=True, null=True,upload_to=product_image_upload_to)
    image3 = models.ImageField(blank=True, null=True,upload_to=product_image_upload_to)
    image4 = models.ImageField(blank=True, null=True,upload_to=product_image_upload_to)

    def __str__(self):
        return self.name
