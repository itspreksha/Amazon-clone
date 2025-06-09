from django.urls import path
from Amazonclone import views

urlpatterns=[
    path('', views.home, name='home'),
    path('product/',views.product_detail,name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('cart/remove/<int:product_id>/',views.remove_from_cart,name='remove_from_cart'),
    path('cart/update/<int:product_id>/',views.update_cart,name='update_cart'),

    
]