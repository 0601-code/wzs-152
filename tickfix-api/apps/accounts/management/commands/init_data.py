from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User
from apps.inventory.models import PartCategory, Part
from apps.repairs.models import ServiceItem


class Command(BaseCommand):
    help = '初始化系统基础数据'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('开始初始化数据...')
        
        self._init_categories()
        self._init_parts()
        self._init_service_items()
        self._init_users()
        
        self.stdout.write(self.style.SUCCESS('数据初始化完成！'))

    def _init_categories(self):
        self.stdout.write('初始化零件分类...')
        categories = [
            ('battery', '电池'),
            ('crown', '表冠'),
            ('crystal', '表镜'),
            ('movement', '机芯配件'),
            ('strap', '表带'),
            ('other', '其他'),
        ]
        for name, _ in categories:
            PartCategory.objects.get_or_create(name=name)
        self.stdout.write(f'  已初始化 {len(categories)} 个零件分类')

    def _init_parts(self):
        self.stdout.write('初始化零件数据...')
        battery_cat = PartCategory.objects.get(name='battery')
        crown_cat = PartCategory.objects.get(name='crown')
        crystal_cat = PartCategory.objects.get(name='crystal')
        movement_cat = PartCategory.objects.get(name='movement')
        
        batteries = [
            {'name': '纽扣电池 SR626SW', 'model_number': 'SR626SW', 'brand': 'Maxell', 
             'unit_price': 15, 'stock_quantity': 50, 'min_stock': 10,
             'compatible_models': '适配大多数石英表，直径6.8mm，厚度2.6mm'},
            {'name': '纽扣电池 SR920SW', 'model_number': 'SR920SW', 'brand': 'Maxell',
             'unit_price': 18, 'stock_quantity': 40, 'min_stock': 10,
             'compatible_models': '适配石英表，直径9.5mm，厚度2.1mm'},
            {'name': '纽扣电池 CR2032', 'model_number': 'CR2032', 'brand': 'Panasonic',
             'unit_price': 12, 'stock_quantity': 60, 'min_stock': 15,
             'compatible_models': '3V锂电池，适用于部分电子表和汽车遥控器'},
            {'name': '纽扣电池 SR621SW', 'model_number': 'SR621SW', 'brand': 'Sony',
             'unit_price': 15, 'stock_quantity': 45, 'min_stock': 10,
             'compatible_models': '直径6.8mm，厚度2.1mm，薄型石英表用'},
            {'name': '纽扣电池 SR44', 'model_number': 'SR44', 'brand': 'Maxell',
             'unit_price': 20, 'stock_quantity': 30, 'min_stock': 8,
             'compatible_models': '1.55V，适用于游标卡尺等精密仪器'},
        ]
        
        crowns = [
            {'name': '不锈钢表冠 通用型', 'model_number': 'CROWN-SS-001', 'brand': '国产',
             'unit_price': 25, 'stock_quantity': 20, 'min_stock': 5,
             'compatible_models': '适配大多数机械表、石英表，螺纹直径3.0mm'},
            {'name': '镀金表冠', 'model_number': 'CROWN-GP-001', 'brand': '国产',
             'unit_price': 45, 'stock_quantity': 15, 'min_stock': 3,
             'compatible_models': '金色表款专用，螺纹直径2.8mm'},
        ]
        
        crystals = [
            {'name': '蓝宝石表镜 圆形 30mm', 'model_number': 'CRY-SAPH-30', 'brand': '国产',
             'unit_price': 80, 'stock_quantity': 10, 'min_stock': 3,
             'compatible_models': '莫氏硬度9，防刮耐磨，直径30.0mm'},
            {'name': '矿物玻璃表镜 圆形 35mm', 'model_number': 'CRY-MIN-35', 'brand': '国产',
             'unit_price': 35, 'stock_quantity': 25, 'min_stock': 5,
             'compatible_models': '普通矿物玻璃，直径35.0mm'},
            {'name': '亚克力表镜 通用', 'model_number': 'CRY-ACRY-GEN', 'brand': '国产',
             'unit_price': 15, 'stock_quantity': 30, 'min_stock': 8,
             'compatible_models': '老款手表用，易抛光，不易碎'},
        ]
        
        movements = [
            {'name': 'ETA2824-2 机芯配件包', 'model_number': 'ETA2824-KIT', 'brand': 'ETA',
             'unit_price': 280, 'stock_quantity': 5, 'min_stock': 2,
             'compatible_models': 'ETA2824-2自动机械机芯易损件套装'},
            {'name': '7S26 机芯配件包', 'model_number': '7S26-KIT', 'brand': 'Seiko',
             'unit_price': 150, 'stock_quantity': 8, 'min_stock': 3,
             'compatible_models': '精工7S26/7S36自动机械机芯易损件套装'},
            {'name': '2035 石英机芯', 'model_number': 'MIYOTA-2035', 'brand': 'Miyota',
             'unit_price': 45, 'stock_quantity': 15, 'min_stock': 5,
             'compatible_models': '美优达2035石英机芯，三针，双历可选'},
        ]
        
        parts_data = []
        for item in batteries:
            parts_data.append({**item, 'category': battery_cat})
        for item in crowns:
            parts_data.append({**item, 'category': crown_cat})
        for item in crystals:
            parts_data.append({**item, 'category': crystal_cat})
        for item in movements:
            parts_data.append({**item, 'category': movement_cat})
        
        count = 0
        for part_data in parts_data:
            if not Part.objects.filter(model_number=part_data['model_number']).exists():
                Part.objects.create(**part_data)
                count += 1
        
        self.stdout.write(f'  已初始化 {count} 个零件')

    def _init_service_items(self):
        self.stdout.write('初始化维修项目...')
        services = [
            {'name': '机械表全面保养', 'description': '机芯拆解清洗、注油、调校、防水测试', 
             'base_price': 300, 'category': 'maintenance'},
            {'name': '石英表换电池', 'description': '更换电池、防水圈清洁、防水测试',
             'base_price': 50, 'category': 'battery'},
            {'name': '挂钟清洗保养', 'description': '机芯清洁、润滑、校准',
             'base_price': 100, 'category': 'cleaning'},
            {'name': '表带调整', 'description': '表带截短、加长、表扣调整',
             'base_price': 30, 'category': 'adjustment'},
            {'name': '外观抛光翻新', 'description': '表壳、表带去划痕抛光',
             'base_price': 150, 'category': 'other'},
            {'name': '更换表镜', 'description': '拆卸旧表镜、清洁、安装新表镜',
             'base_price': 50, 'category': 'repair'},
            {'name': '更换表冠', 'description': '更换表冠及防水圈',
             'base_price': 60, 'category': 'repair'},
            {'name': '机芯维修', 'description': '机芯故障检测与维修',
             'base_price': 200, 'category': 'repair'},
        ]
        
        count = 0
        for service_data in services:
            if not ServiceItem.objects.filter(name=service_data['name']).exists():
                ServiceItem.objects.create(**service_data)
                count += 1
        
        self.stdout.write(f'  已初始化 {count} 个维修项目')

    def _init_users(self):
        self.stdout.write('初始化用户账号...')
        
        users = [
            {'username': 'admin', 'password': 'admin123456', 'email': 'admin@tickfix.com',
             'phone': '13800138000', 'role': 'admin', 'employee_id': 'A001', 'is_staff': True, 'is_superuser': True},
            {'username': 'reception', 'password': 'reception123', 'email': 'reception@tickfix.com',
             'phone': '13800138001', 'role': 'receptionist', 'employee_id': 'R001'},
            {'username': 'tech01', 'password': 'tech123456', 'email': 'tech01@tickfix.com',
             'phone': '13800138002', 'role': 'technician', 'employee_id': 'T001'},
            {'username': 'cashier', 'password': 'cashier123', 'email': 'cashier@tickfix.com',
             'phone': '13800138003', 'role': 'cashier', 'employee_id': 'C001'},
        ]
        
        count = 0
        for user_data in users:
            if not User.objects.filter(username=user_data['username']).exists():
                password = user_data.pop('password')
                user = User.objects.create(**user_data)
                user.set_password(password)
                user.save()
                count += 1
        
        self.stdout.write(f'  已初始化 {count} 个用户账号')
        self.stdout.write('  默认账号:')
        self.stdout.write('    管理员: admin / admin123456')
        self.stdout.write('    前台接件员: reception / reception123')
        self.stdout.write('    维修技师: tech01 / tech123456')
        self.stdout.write('    收银员: cashier / cashier123')
