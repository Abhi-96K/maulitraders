from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, StockAdjustmentLog

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'brand', 'category', 'retail_price', 'stock_quantity', 'is_active', 'is_featured', 'display_order']
    list_filter = ['brand', 'category', 'is_active', 'is_featured']
    list_editable = ['is_featured', 'display_order']
    search_fields = ['name', 'sku', 'description']
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug': ('name',)}

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_order']
    list_editable = ['display_order']
    prepopulated_fields = {'slug': ('name',)}

class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'show_on_home']
    list_editable = ['show_on_home']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(StockAdjustmentLog)
