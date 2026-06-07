from django.contrib import admin
from .models import PartCategory, Part, StockRecord


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_number', 'brand', 'category', 'unit_price', 'stock_quantity', 'is_low_stock')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'model_number', 'brand')
    readonly_fields = ('is_low_stock',)


@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = ('part', 'type', 'quantity', 'reference', 'operator', 'created_at')
    list_filter = ('type',)
    search_fields = ('part__name', 'reference')
    readonly_fields = ('created_at',)
