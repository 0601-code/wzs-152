from django.db import models, transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PartCategory, Part, StockRecord
from .serializers import (
    PartCategorySerializer, PartSerializer, 
    PartListSerializer, StockRecordSerializer
)


class PartCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PartCategory.objects.all()
    serializer_class = PartCategorySerializer


class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.all()
    filterset_fields = ['category', 'brand']
    search_fields = ['name', 'model_number', 'brand']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PartListSerializer
        return PartSerializer
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        parts = Part.objects.filter(stock_quantity__lte=models.F('min_stock'))
        serializer = PartListSerializer(parts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        part = self.get_object()
        quantity = request.data.get('quantity', 0)
        remark = request.data.get('remark', '')
        
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({'error': '数量必须是整数'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            part.stock_quantity += quantity
            part.save()
            
            StockRecord.objects.create(
                part=part,
                type='adjust' if quantity < 0 else 'in',
                quantity=abs(quantity),
                remark=remark,
                operator=request.user
            )
        
        serializer = self.get_serializer(part)
        return Response(serializer.data)


class StockRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockRecord.objects.all()
    serializer_class = StockRecordSerializer
    filterset_fields = ['part', 'type']
    ordering_fields = ['created_at']
