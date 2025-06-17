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
    sizes=models.CharField(max_length=100,blank=True)
    colors=models.CharField(max_length=100,blank=True)
    specifications=models.TextField(blank=True)
    rating=models.FloatField(default=0.0)
    


    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class OTPVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - OTP"

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    order_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=[("Pending","Pending"),("Shipped","Shipped"),("Delivered","Delivered")])
    total_price=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1) 

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i,i) for i in range(1,6)])
    comment=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by{self.user.username}'s Review on {self.product.name}"
    
class ProductQuestion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    answer=models.TextField(blank=True,null=True)
    asked_at=models.DateTimeField(auto_now_add=True)
    answered_at=models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f"Q by {self.user.username} on {self.product.name}"
