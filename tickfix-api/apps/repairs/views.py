from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import (
    RepairStatus, ServiceItem, RepairOrder, 
    StatusHistory, RepairOrderService, RepairPartUsage
)
from .serializers import (
    ServiceItemSerializer, RepairOrderListSerializer, RepairOrderSerializer,
    StatusHistorySerializer, StatusTransitionSerializer,
    RepairPartUsageSerializer, PartUsageCreateSerializer
)
from apps.inventory.models import Part


class ServiceItemViewSet(viewsets.ModelViewSet):
    queryset = ServiceItem.objects.all()
    serializer_class = ServiceItemSerializer
    filterset_fields = ['category', 'is_active']
    search_fields = ['name']


class RepairOrderViewSet(viewsets.ModelViewSet):
    queryset = RepairOrder.objects.all()
    filterset_fields = ['status', 'watch_type', 'technician']
    search_fields = ['order_no', 'brand', 'model', 'customer_name', 'customer_phone', 'pickup_code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RepairOrderListSerializer
        return RepairOrderSerializer
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        order = self.get_object()
        serializer = StatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['new_status']
        remark = serializer.validated_data.get('remark', '')
        
        if not order.can_transition_to(new_status):
            return Response(
                {'error': f'无法从 {order.get_status_display()} 转换到 {dict(RepairStatus.CHOICES)[new_status]}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            if 'inspection_report' in serializer.validated_data:
                order.inspection_report = serializer.validated_data['inspection_report']
            if 'quote_remark' in serializer.validated_data:
                order.quote_remark = serializer.validated_data['quote_remark']
            if 'estimated_cost' in serializer.validated_data:
                order.estimated_cost = serializer.validated_data['estimated_cost']
            if 'labor_cost' in serializer.validated_data:
                order.labor_cost = serializer.validated_data['labor_cost']
            
            if new_status == RepairStatus.READY_FOR_PICKUP:
                order.final_cost = order.parts_cost + order.labor_cost
            
            order.transition_status(new_status, request.user, remark)
        
        return Response(RepairOrderSerializer(order).data)
    
    @action(detail=True, methods=['post'])
    def add_part_usage(self, request, pk=None):
        order = self.get_object()
        
        allowed_statuses = [
            RepairStatus.CUSTOMER_APPROVED,
            RepairStatus.REPAIRING,
            RepairStatus.PARTS_OUT,
        ]
        if order.status not in allowed_statuses:
            return Response(
                {'error': f'当前状态({order.get_status_display()})不允许添加零件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PartUsageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        part_id = serializer.validated_data['part_id']
        quantity = serializer.validated_data['quantity']
        remark = serializer.validated_data.get('remark', '')
        
        try:
            part = Part.objects.get(id=part_id)
        except Part.DoesNotExist:
            return Response({'error': '零件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        if part.stock_quantity < quantity:
            return Response({'error': '库存不足'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            part_usage = RepairPartUsage.objects.create(
                order=order,
                part=part,
                quantity=quantity,
                unit_price=part.unit_price,
                operator=request.user,
                remark=remark
            )
            
            order.parts_cost += part.unit_price * quantity
            order.save()
            
            if order.status == RepairStatus.REPAIRING:
                order.transition_status(RepairStatus.PARTS_OUT, request.user, '零件出库')
        
        return Response(RepairPartUsageSerializer(part_usage).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def by_pickup_code(self, request):
        pickup_code = request.query_params.get('code')
        if not pickup_code:
            return Response({'error': '请提供取件码'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = RepairOrder.objects.get(pickup_code=pickup_code)
            return Response(RepairOrderSerializer(order).data)
        except RepairOrder.DoesNotExist:
            return Response({'error': '未找到对应接件单'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        total = RepairOrder.objects.count()
        pending = RepairOrder.objects.filter(status=RepairStatus.PENDING).count()
        repairing = RepairOrder.objects.filter(status__in=[
            RepairStatus.INSPECTING, RepairStatus.REPAIRING, RepairStatus.PARTS_OUT
        ]).count()
        ready = RepairOrder.objects.filter(status=RepairStatus.READY_FOR_PICKUP).count()
        completed = RepairOrder.objects.filter(status=RepairStatus.COMPLETED).count()
        
        return Response({
            'total': total,
            'pending': pending,
            'repairing': repairing,
            'ready_for_pickup': ready,
            'completed': completed
        })


class StatusHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StatusHistory.objects.all()
    serializer_class = StatusHistorySerializer
    filterset_fields = ['order']
