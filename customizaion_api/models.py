from django.db import models

class ProductCategories(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, related_name='products')
    
    def __str__(self):
        return self.name