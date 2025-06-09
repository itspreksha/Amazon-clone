from django.urls import path
from Amazonclone import views

urlpatterns=[
    path('', views.home, name='home'),
    path('product/',views.product_detail,name='product_detail'),
    
]