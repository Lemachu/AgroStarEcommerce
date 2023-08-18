from django.contrib import admin
from .models import Product, ProductGallery, ReviewRating
import admin_thumbnails
# Register your models here.

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock','category', 'prodavac', 'created_date', 'modified_date', 'is_availible')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)