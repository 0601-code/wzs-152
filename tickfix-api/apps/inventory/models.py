from django.db import models


class PartCategory(models.Model):
    CATEGORY_CHOICES = (
        ('battery', '电池'),
        ('crown', '表冠'),
        ('crystal', '表镜'),
        ('movement', '机芯配件'),
        ('strap', '表带'),
        ('other', '其他'),
    )
    
    name = models.CharField('分类名称', max_length=50, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField('描述', blank=True)

    class Meta:
        db_table = 'tf_part_category'
        verbose_name = '零件分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.get_name_display()


class Part(models.Model):
    category = models.ForeignKey(PartCategory, on_delete=models.PROTECT, verbose_name='分类')
    name = models.CharField('零件名称', max_length=200)
    model_number = models.CharField('型号规格', max_length=200)
    brand = models.CharField('品牌', max_length=100, blank=True)
    compatible_models = models.TextField('适配说明', blank=True)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.IntegerField('库存数量', default=0)
    min_stock = models.IntegerField('最低库存预警', default=5)
    location = models.CharField('存放位置', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'tf_part'
        verbose_name = '零件'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.model_number})'

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock


class StockRecord(models.Model):
    TYPE_CHOICES = (
        ('in', '入库'),
        ('out', '出库'),
        ('adjust', '库存调整'),
    )
    
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='stock_records', verbose_name='零件')
    type = models.CharField('类型', max_length=10, choices=TYPE_CHOICES)
    quantity = models.IntegerField('数量')
    reference = models.CharField('关联单号', max_length=100, blank=True)
    remark = models.TextField('备注', blank=True)
    operator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'tf_stock_record'
        verbose_name = '库存记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_type_display()} - {self.part.name} x {self.quantity}'
