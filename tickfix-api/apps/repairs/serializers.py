from rest_framework import serializers
from .models import (
    RepairStatus, ServiceItem, RepairOrder, 
    StatusHistory, RepairOrderService, RepairPartUsage
)
from apps.inventory.serializers import PartSerializer
from apps.accounts.serializers import UserSerializer


class ServiceItemSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = ServiceItem
        fields = ['id', 'name', 'description', 'base_price', 'category', 'category_display', 'is_active']


class RepairOrderServiceSerializer(serializers.ModelSerializer):
    service_item_info = ServiceItemSerializer(source='service_item', read_only=True)
    
    class Meta:
        model = RepairOrderService
        fields = ['id', 'service_item', 'service_item_info', 'quantity', 'unit_price', 'remark']


class RepairPartUsageSerializer(serializers.ModelSerializer):
    part_info = PartSerializer(source='part', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = RepairPartUsage
        fields = ['id', 'part', 'part_info', 'quantity', 'unit_price', 'operator', 'operator_name', 'out_at', 'remark']
        read_only_fields = ['id', 'out_at']


class StatusHistorySerializer(serializers.ModelSerializer):
    from_status_display = serializers.CharField(source='get_from_status_display', read_only=True)
    to_status_display = serializers.CharField(source='get_to_status_display', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = StatusHistory
        fields = ['id', 'from_status', 'from_status_display', 'to_status', 'to_status_display', 
                  'operator', 'operator_name', 'remark', 'created_at']


class RepairOrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    watch_type_display = serializers.CharField(source='get_watch_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    technician_name = serializers.CharField(source='technician.username', read_only=True, allow_null=True)
    
    class Meta:
        model = RepairOrder
        fields = [
            'id', 'order_no', 'watch_type', 'watch_type_display',
            'brand', 'model', 'customer_name', 'customer_phone',
            'status', 'status_display', 'estimated_cost', 'final_cost',
            'pickup_code', 'created_by', 'created_by_name',
            'technician', 'technician_name', 'created_at', 'updated_at'
        ]


class RepairOrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    watch_type_display = serializers.CharField(source='get_watch_type_display', read_only=True)
    next_statuses = serializers.SerializerMethodField()
    created_by_info = UserSerializer(source='created_by', read_only=True)
    technician_info = UserSerializer(source='technician', read_only=True)
    order_services = RepairOrderServiceSerializer(many=True, required=False)
    part_usages = RepairPartUsageSerializer(many=True, read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = RepairOrder
        fields = [
            'id', 'order_no', 'watch_type', 'watch_type_display',
            'brand', 'model', 'serial_number', 'appearance_flaws',
            'fault_description', 'customer_name', 'customer_phone',
            'pickup_code', 'estimated_cost', 'final_cost', 'parts_cost',
            'labor_cost', 'status', 'status_display', 'next_statuses',
            'inspection_report', 'quote_remark', 'repair_remark',
            'created_by', 'created_by_info', 'technician', 'technician_info',
            'order_services', 'part_usages', 'status_history',
            'created_at', 'updated_at', 'completed_at', 'picked_up_at'
        ]
        read_only_fields = ['id', 'order_no', 'pickup_code', 'created_at', 'updated_at', 'completed_at', 'picked_up_at']
    
    def get_next_statuses(self, obj):
        next_statuses = obj.get_next_statuses()
        return [
            {'value': s, 'label': dict(RepairStatus.CHOICES)[s]}
            for s in next_statuses
        ]
    
    def create(self, validated_data):
        order_services_data = validated_data.pop('order_services', [])
        validated_data['created_by'] = self.context['request'].user
        order = RepairOrder.objects.create(**validated_data)
        
        for service_data in order_services_data:
            RepairOrderService.objects.create(order=order, **service_data)
        
        return order


class StatusTransitionSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=RepairStatus.CHOICES)
    remark = serializers.CharField(required=False, allow_blank=True)
    inspection_report = serializers.CharField(required=False, allow_blank=True)
    quote_remark = serializers.CharField(required=False, allow_blank=True)
    estimated_cost = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    labor_cost = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)


class PartUsageCreateSerializer(serializers.Serializer):
    part_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    remark = serializers.CharField(required=False, allow_blank=True)
