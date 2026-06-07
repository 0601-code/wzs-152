from django.contrib import admin
from .models import ServiceItem, RepairOrder, StatusHistory, RepairOrderService, RepairPartUsage


class RepairOrderServiceInline(admin.TabularInline):
    model = RepairOrderService
    extra = 0


class RepairPartUsageInline(admin.TabularInline):
    model = RepairPartUsage
    extra = 0
    readonly_fields = ('out_at',)


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'operator', 'remark', 'created_at')


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)


@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'brand', 'model', 'customer_name', 'customer_phone', 
                    'status', 'estimated_cost', 'final_cost', 'pickup_code', 'created_at')
    list_filter = ('status', 'watch_type', 'technician')
    search_fields = ('order_no', 'brand', 'model', 'customer_name', 'customer_phone', 'pickup_code')
    readonly_fields = ('order_no', 'pickup_code', 'created_at', 'updated_at', 'completed_at', 'picked_up_at')
    inlines = [RepairOrderServiceInline, RepairPartUsageInline, StatusHistoryInline]


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'from_status', 'to_status', 'operator', 'created_at')
    list_filter = ('from_status', 'to_status')
    search_fields = ('order__order_no',)
    readonly_fields = ('created_at',)
