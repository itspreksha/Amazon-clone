from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import check_and_notify_stock 
from django.core.mail import send_mail
from decimal import Decimal
from django.db.models import Avg
# Create your models here.
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('books', 'Books'),
        ('appliances', 'Appliances'),
    ]

    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Fixed base price
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 👈 Changed from FloatField
    description = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(auto_now_add=True)
    sizes = models.CharField(max_length=100, blank=True)
    colors = models.CharField(max_length=100, blank=True)
    specifications = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)
    stock = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        notify = False
        if self.pk:
            old = Product.objects.get(pk=self.pk)
            if old.stock == 0 and self.stock > 0:
                notify = True
        super().save(*args, **kwargs)
        if notify:
            self.notify_waiting_users()

    def notify_waiting_users(self):
        from .models import StockNotification  # Assuming it's in the same app
        notifications = StockNotification.objects.filter(product=self, notified=False)
        for note in notifications:
            send_mail(
                subject='Item Back in Stock!',
                message=f'Hi {note.user.username}, the product "{self.name}" is now available!',
                from_email='itspreksha54@gmail.com',
                recipient_list=[note.user.email],
                html_message=f'<p>Hi {note.user.username},</p><p><strong>{self.name}</strong> is now back in stock!</p><p><a href="https://yourdomain.com/product/{self.id}">Buy Now</a></p>'
            )
            note.notified = True
            note.save()

    def update_rating(self):
        avg_rating = self.reviews.aggregate(avg=Avg('rating'))['avg']
        self.rating = round(avg_rating or 0.0, 2)
        self.save(update_fields=['rating'])

    def register_view(self):
        self.view_count += 1

        # 🔁 Price increases 1% every 10 views, max 2x
        increase_factor = Decimal("1.00") + (Decimal(self.view_count) // Decimal("10")) * Decimal("0.01")
        increase_factor = min(increase_factor, Decimal("2.00"))

        self.price = (self.base_price * increase_factor).quantize(Decimal("0.01"))
        self.save(update_fields=['view_count', 'price'])
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    address=models.TextField(blank=True)
    default_address=models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='profiles_with_default'
    )
    is_blocked=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username}'s Profile"

class OTPVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - OTP"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Shipped", "Shipped"), ("Delivered", "Delivered")],
        default="Pending"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Payment-related fields (only define ONCE!)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    payment_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  # for 'pay_xxx'
    payment_method = models.CharField(max_length=20, default='Online')  # 'Online' or 'COD'
    payment_status = models.CharField(max_length=20, default='Pending')  # 'Pending', 'Success', etc.

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1) 

def review_image_upload_path(instance, filename):
    return f'reviews/user_{instance.user.id}/{filename}'
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1 to 5
    comment = models.TextField()
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

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

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    phone=models.CharField(max_length=10)
    pincode=models.CharField(max_length=10)
    address_line=models.TextField()
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    address_type=models.CharField(max_length=10,choices=[('Home','Home'),('Office','Office')])
    is_default=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}-{self.city}"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, blank=True, null=True)  # Ensure this exists
    color = models.CharField(max_length=50, blank=True, null=True)  # Ensure this exists
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username}-{self.product.name}"
    
class StockAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    notified=models.BooleanField(default=False)

class StockNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


@receiver(post_save,sender=Product)
def trigger_stock_notification(sender,instance,**kwargs):
    if instance.stock>0:
        check_and_notify_stock(instance)

class UserLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.city}, {self.country}"