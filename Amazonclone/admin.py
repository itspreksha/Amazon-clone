from django.contrib import admin
from .models import Product
from .models import ProductQuestion,Profile,OTPVerification,Order,OrderItem,Review,Address,Cart

@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'question_text', 'asked_at']
    search_fields = ['question_text', 'user__username', 'product__name']

admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(OTPVerification)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Address)
admin.site.register(Cart)


# Register your models here.
