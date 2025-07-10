from django.db import models

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