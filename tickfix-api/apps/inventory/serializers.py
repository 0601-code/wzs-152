from rest_framework import serializers
from .models import PartCategory, Part, StockRecord


class PartCategorySerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = PartCategory
        fields = ['id', 'name', 'name_display', 'description']


class PartSerializer(serializers.ModelSerializer):
    category_info = PartCategorySerializer(source='category', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Part
        fields = [
            'id', 'category', 'category_info', 'name', 'model_number',
            'brand', 'compatible_models', 'unit_price', 'stock_quantity',
            'min_stock', 'location', 'is_low_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PartListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.get_name_display', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Part
        fields = [
            'id', 'name', 'model_number', 'brand', 'category_name',
            'unit_price', 'stock_quantity', 'is_low_stock', 'location',
            'compatible_models'
        ]


class StockRecordSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = StockRecord
        fields = [
            'id', 'part', 'part_name', 'type', 'type_display',
            'quantity', 'reference', 'remark', 'operator', 'operator_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
