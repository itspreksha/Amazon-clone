from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Product(models.Model):
    Category_choices= [
        ('electronics' , 'Electronics'),
        ('fashion','Fashion'),
        ('books','Books'),
        ('appliances','Appliances'),

    ]
    name = models.CharField(max_length=100)
    price=models.FloatField()
    description=models.TextField()
    category=models.CharField(max_length=100,choices=Category_choices)
    image=models.ImageField(upload_to='images/')
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    order_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=[("Pending","Pending"),("Shipped","Shipped"),("Delivered","Delivered")])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2)
