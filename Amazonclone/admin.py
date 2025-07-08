from django.contrib import admin
from .models import Product
from .models import ProductQuestion,Profile,OTPVerification,Order,OrderItem,Review,Address,Cart
from django.utils.html import format_html
from django.db.models import Sum,Count
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


class DashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/dashboard.html"

    def changelist_view(self, request, extra_context=None):
        total_users = User.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0.00

        # Chart data
        order_status_counts = (
            Order.objects.values('status')
            .annotate(count=Count('status'))
        )

        payment_method_counts = (
            Order.objects.values('payment_method')
            .annotate(count=Count('payment_method'))
        )

        extra_context = {
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'order_status_counts': list(order_status_counts),
            'payment_method_counts': list(payment_method_counts),
        }
        return super().changelist_view(request, extra_context=extra_context)

# Hook dashboard into content types
#admin.site.unregister(ContentType)
admin.site.register(ContentType, DashboardAdmin)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['name','price','category','created_at','rating']
    list_filter=['category']
    search_fields=['name','description','category']

@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'question_text', 'asked_at']
    search_fields = ['question_text', 'user__username', 'product__name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user','phone','city','email_verified','is_blocked']
    list_filter=['email_verified']
    search_fields=['user__username','phone']
    list_editable=['is_blocked']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'payment_status', 'total_price', 'order_date']
    list_filter = ['status', 'payment_status']
    search_fields = ['user__username', 'razorpay_order_id', 'payment_id']
    list_editable = ['status', 'payment_status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','product_name','price','quantity']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=['product','user','rating','created_at']
    list_filter=['rating']

@admin.register(Address)
class AdressAdmin(admin.ModelAdmin):
    list_display=['user','name','city','state','pincode','is_default']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display=['user','product','quantity','size','color']
