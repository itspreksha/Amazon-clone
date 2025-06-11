from django.urls import path
from Amazonclone import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView


urlpatterns=[
    path('', views.home, name='home'),
    path('product/',views.product_detail,name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('cart/remove/<int:product_id>/',views.remove_from_cart,name='remove_from_cart'),
    path('cart/update/<int:product_id>/',views.update_cart,name='update_cart'),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', views.profile_view, name='profile'),
    path('orders/', views.order_history, name='order_history'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.update_password_view, name='change_password'),
    
]