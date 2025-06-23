from django.urls import path,reverse
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .views import (
    home, product_detail, cart_view, add_to_cart, remove_from_cart, update_cart,
    order_history, register_view, login_view, logout_view,
    update_password_view, verify_otp_view, resend_otp, session_expired,
    CustomPasswordResetView
)
from .views import CustomPasswordResetView
from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
urlpatterns = [
    path('', home, name='home'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('cart/', cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', update_cart, name='update_cart'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='Amazonclone/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='Amazonclone/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='Amazonclone/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('set-default-address/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('addresses/',views.manage_addresses,name='manage_addresses'),
    path('addresses/add/',views.add_address,name='add_address'),
    path('addresses/edit/<int:address_id>/',views.edit_address,name='edit_address'),
    path('profile/',views.view_profile, name='view_profile'),
    path('profile/edit/',views.edit_profile,name='edit_profile'),
    path('profile/change-password/',views.change_password,name='change_password'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/reorder/<int:order_id>/',views.reorder,name='reorder'),
    path('order-success/', views.order_success, name='order_success'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', update_password_view, name='change_password'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('session-expired/', session_expired, name='session_expired'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/',views.payment_success,name='payment_success'),
    path('payment/success/', views.payment_success, name='order_success'),
    path('payment/success/',views.cod_success_view,name='cod_success'),
    path('cod-order/',views.cod_order,name='cod_order'),
    path('thankyou/', views.thankyou, name='thankyou'),
    path('checkout/', views.checkout, name='checkout'),
    path('check-cod/',views.check_cod_availability,name='check_cod_availability'),
    path('cod/success/', views.cod_success_view, name='cod_success'),

]   
