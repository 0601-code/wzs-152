import random
import string
from django.db import models
from django.db import transaction
from django.utils import timezone


class RepairStatus:
    PENDING = 'pending'
    INSPECTING = 'inspecting'
    QUOTED = 'quoted'
    CUSTOMER_APPROVED = 'customer_approved'
    CUSTOMER_REJECTED = 'customer_rejected'
    REPAIRING = 'repairing'
    PARTS_OUT = 'parts_out'
    REPAIRED = 'repaired'
    READY_FOR_PICKUP = 'ready_for_pickup'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    CHOICES = (
        (PENDING, '待检测'),
        (INSPECTING, '检测中'),
        (QUOTED, '已报价待确认'),
        (CUSTOMER_APPROVED, '客户同意'),
        (CUSTOMER_REJECTED, '客户拒绝'),
        (REPAIRING, '维修中'),
        (PARTS_OUT, '零件出库'),
        (REPAIRED, '维修完成'),
        (READY_FOR_PICKUP, '待取件'),
        (COMPLETED, '已完成'),
        (CANCELLED, '已取消'),
    )

    TRANSITIONS = {
        PENDING: [INSPECTING, CANCELLED],
        INSPECTING: [QUOTED, CANCELLED],
        QUOTED: [CUSTOMER_APPROVED, CUSTOMER_REJECTED, CANCELLED],
        CUSTOMER_APPROVED: [REPAIRING, CANCELLED],
        CUSTOMER_REJECTED: [CANCELLED],
        REPAIRING: [PARTS_OUT, REPAIRED, CANCELLED],
        PARTS_OUT: [REPAIRING, REPAIRED, CANCELLED],
        REPAIRED: [READY_FOR_PICKUP, CANCELLED],
        READY_FOR_PICKUP: [COMPLETED, CANCELLED],
        COMPLETED: [],
        CANCELLED: [],
    }

    @classmethod
    def can_transition(cls, from_status, to_status):
        return to_status in cls.TRANSITIONS.get(from_status, [])

    @classmethod
    def get_next_statuses(cls, current_status):
        return cls.TRANSITIONS.get(current_status, [])


class ServiceItem(models.Model):
    name = models.CharField('项目名称', max_length=200)
    description = models.TextField('项目描述', blank=True)
    base_price = models.DecimalField('基础价格', max_digits=10, decimal_places=2, default=0)
    category = models.CharField('分类', max_length=50, choices=(
        ('maintenance', '保养'),
        ('battery', '换电池'),
        ('cleaning', '清洗'),
        ('adjustment', '调整'),
        ('repair', '维修'),
        ('other', '其他'),
    ), default='repair')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'tf_service_item'
        verbose_name = '维修项目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class RepairOrder(models.Model):
    WATCH_TYPE_CHOICES = (
        ('mechanical', '机械表'),
        ('quartz', '石英表'),
        ('wall', '挂钟'),
        ('pocket', '怀表'),
        ('other', '其他'),
    )

    order_no = models.CharField('接件单号', max_length=32, unique=True, editable=False)
    watch_type = models.CharField('钟表类型', max_length=20, choices=WATCH_TYPE_CHOICES)
    brand = models.CharField('品牌', max_length=100)
    model = models.CharField('型号', max_length=200, blank=True)
    serial_number = models.CharField('序列号', max_length=200, blank=True)
    appearance_flaws = models.TextField('外观瑕疵', blank=True)
    fault_description = models.TextField('故障描述')
    customer_name = models.CharField('客户姓名', max_length=100)
    customer_phone = models.CharField('客户电话', max_length=20)
    pickup_code = models.CharField('取件码', max_length=8, unique=True, editable=False)
    
    estimated_cost = models.DecimalField('预估费用', max_digits=10, decimal_places=2, default=0)
    final_cost = models.DecimalField('最终费用', max_digits=10, decimal_places=2, default=0)
    parts_cost = models.DecimalField('零件费用', max_digits=10, decimal_places=2, default=0)
    labor_cost = models.DecimalField('工时费用', max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField('维修状态', max_length=30, choices=RepairStatus.CHOICES, default=RepairStatus.PENDING)
    inspection_report = models.TextField('检测报告', blank=True)
    quote_remark = models.TextField('报价说明', blank=True)
    repair_remark = models.TextField('维修备注', blank=True)
    
    service_items = models.ManyToManyField(ServiceItem, through='RepairOrderService', verbose_name='维修项目')
    
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='created_orders', verbose_name='接件人')
    technician = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders', verbose_name='维修技师')
    created_at = models.DateTimeField('接件时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    picked_up_at = models.DateTimeField('取件时间', null=True, blank=True)

    class Meta:
        db_table = 'tf_repair_order'
        verbose_name = '接件单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_no} - {self.brand} {self.model}'

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = self._generate_order_no()
        if not self.pickup_code:
            self.pickup_code = self._generate_pickup_code()
        super().save(*args, **kwargs)

    def _generate_order_no(self):
        date_str = timezone.now().strftime('%Y%m%d')
        last_order = RepairOrder.objects.filter(
            order_no__startswith=f'TF{date_str}'
        ).order_by('-order_no').first()
        if last_order:
            seq = int(last_order.order_no[-4:]) + 1
        else:
            seq = 1
        return f'TF{date_str}{seq:04d}'

    def _generate_pickup_code(self):
        while True:
            code = ''.join(random.choices(string.digits, k=6))
            if not RepairOrder.objects.filter(pickup_code=code).exists():
                return code

    def can_transition_to(self, new_status):
        return RepairStatus.can_transition(self.status, new_status)

    def get_next_statuses(self):
        return RepairStatus.get_next_statuses(self.status)

    @transaction.atomic
    def transition_status(self, new_status, operator, remark=''):
        if not self.can_transition_to(new_status):
            raise ValueError(f'不能从 {self.get_status_display()} 转换到 {dict(RepairStatus.CHOICES).get(new_status, new_status)}')
        
        old_status = self.status
        self.status = new_status
        
        if new_status == RepairStatus.COMPLETED:
            self.completed_at = timezone.now()
        if new_status == RepairStatus.READY_FOR_PICKUP and not self.picked_up_at:
            pass
        
        self.save()
        
        StatusHistory.objects.create(
            order=self,
            from_status=old_status,
            to_status=new_status,
            operator=operator,
            remark=remark
        )
        
        return True


class StatusHistory(models.Model):
    order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, related_name='status_history', verbose_name='接件单')
    from_status = models.CharField('原状态', max_length=30, choices=RepairStatus.CHOICES)
    to_status = models.CharField('新状态', max_length=30, choices=RepairStatus.CHOICES)
    operator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'tf_status_history'
        verbose_name = '状态流转记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order.order_no}: {self.get_from_status_display()} → {self.get_to_status_display()}'


class RepairOrderService(models.Model):
    order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, related_name='order_services')
    service_item = models.ForeignKey(ServiceItem, on_delete=models.PROTECT, verbose_name='服务项目')
    quantity = models.IntegerField('数量', default=1)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    remark = models.TextField('备注', blank=True)

    class Meta:
        db_table = 'tf_repair_order_service'
        verbose_name = '接件单服务项目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.order.order_no} - {self.service_item.name}'


class RepairPartUsage(models.Model):
    order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, related_name='part_usages', verbose_name='接件单')
    part = models.ForeignKey('inventory.Part', on_delete=models.PROTECT, verbose_name='零件')
    quantity = models.IntegerField('数量', default=1)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    operator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='出库人')
    out_at = models.DateTimeField('出库时间', auto_now_add=True)
    remark = models.TextField('备注', blank=True)

    class Meta:
        db_table = 'tf_repair_part_usage'
        verbose_name = '零件消耗记录'
        verbose_name_plural = verbose_name
        ordering = ['-out_at']

    def __str__(self):
        return f'{self.order.order_no} - {self.part.name} x {self.quantity}'

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            from apps.inventory.models import StockRecord
            self.part.stock_quantity -= self.quantity
            self.part.save()
            StockRecord.objects.create(
                part=self.part,
                type='out',
                quantity=self.quantity,
                reference=self.order.order_no,
                remark=f'维修出库: {self.order.order_no}',
                operator=self.operator
            )
