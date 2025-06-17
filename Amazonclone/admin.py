from django.contrib import admin
from .models import Product
from .models import ProductQuestion

@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'question_text', 'asked_at']
    search_fields = ['question_text', 'user__username', 'product__name']

admin.site.register(Product)
# Register your models here.
