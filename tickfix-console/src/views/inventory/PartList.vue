<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">零件仓库</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>新增零件
      </el-button>
    </div>

    <div class="card-wrapper">
      <div class="filter-bar">
        <el-input
          v-model="filters.search"
          placeholder="搜索零件名称/型号/品牌"
          clearable
          style="width: 280px"
          @keyup.enter="loadParts"
        />
        <el-select v-model="filters.category" placeholder="分类" clearable style="width: 160px">
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name_display"
            :value="cat.id"
          />
        </el-select>
        <el-button type="primary" @click="loadParts">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="warning" @click="loadLowStock">库存预警</el-button>
      </div>

      <el-table :data="parts" v-loading="loading" border>
        <el-table-column prop="name" label="零件名称" min-width="180" />
        <el-table-column prop="model_number" label="型号规格" width="160" />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column label="单价" width="100">
          <template #default="{ row }">¥{{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column label="库存" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_low_stock ? 'danger' : 'success'">
              {{ row.stock_quantity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="存放位置" width="120" />
        <el-table-column prop="compatible_models" label="适配说明" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleAdjust(row)">调库存</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadParts"
          @current-change="loadParts"
        />
      </div>
    </div>

    <el-dialog v-model="showAddDialog" title="新增零件" width="600px">
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="addForm.category" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="cat in categories"
                  :key="cat.id"
                  :label="cat.name_display"
                  :value="cat.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="零件名称" prop="name">
              <el-input v-model="addForm.name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="型号规格" prop="model_number">
              <el-input v-model="addForm.model_number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品牌">
              <el-input v-model="addForm.brand" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number v-model="addForm.unit_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="库存数量" prop="stock_quantity">
              <el-input-number v-model="addForm.stock_quantity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最低预警">
              <el-input-number v-model="addForm.min_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="存放位置">
          <el-input v-model="addForm.location" />
        </el-form-item>
        <el-form-item label="适配说明">
          <el-input v-model="addForm.compatible_models" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="addLoading" @click="handleAddSubmit">确认</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAdjustDialog" title="调整库存" width="400px">
      <el-form label-width="100px">
        <el-form-item label="零件名称">
          <span>{{ adjustPart?.name }}</span>
        </el-form-item>
        <el-form-item label="当前库存">
          <el-tag type="info">{{ adjustPart?.stock_quantity }}</el-tag>
        </el-form-item>
        <el-form-item label="调整数量">
          <el-input-number v-model="adjustForm.quantity" :min="-999999" />
          <div style="margin-top: 6px; color: #909399; font-size: 12px">正数增加，负数减少</div>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="adjustForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdjustDialog = false">取消</el-button>
        <el-button type="primary" :loading="adjustLoading" @click="handleAdjustSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getParts, getPartCategories, createPart, adjustStock, getLowStockParts } from '@/api/inventory'

const parts = ref([])
const categories = ref([])
const loading = ref(false)
const addLoading = ref(false)
const adjustLoading = ref(false)

const showAddDialog = ref(false)
const showAdjustDialog = ref(false)
const adjustPart = ref(null)
const addFormRef = ref(null)

const filters = reactive({
  search: '',
  category: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const addForm = reactive({
  category: '',
  name: '',
  model_number: '',
  brand: '',
  unit_price: 0,
  stock_quantity: 0,
  min_stock: 5,
  location: '',
  compatible_models: ''
})

const adjustForm = reactive({
  quantity: 0,
  remark: ''
})

const addRules = {
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  name: [{ required: true, message: '请输入零件名称', trigger: 'blur' }],
  model_number: [{ required: true, message: '请输入型号规格', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  stock_quantity: [{ required: true, message: '请输入库存数量', trigger: 'blur' }]
}

const loadCategories = async () => {
  try {
    const data = await getPartCategories()
    categories.value = data.results || data
  } catch (error) {
    console.error(error)
  }
}

const loadParts = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    if (!params.search) delete params.search
    if (!params.category) delete params.category
    
    const data = await getParts(params)
    parts.value = data.results || []
    pagination.total = data.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadLowStock = async () => {
  try {
    loading.value = true
    const data = await getLowStockParts()
    parts.value = data
    pagination.total = data.length
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.category = ''
  pagination.page = 1
  loadParts()
}

const handleEdit = (row) => {
  ElMessage.info('编辑功能待实现')
}

const handleAdjust = (row) => {
  adjustPart.value = row
  adjustForm.quantity = 0
  adjustForm.remark = ''
  showAdjustDialog.value = true
}

const handleAdjustSubmit = async () => {
  try {
    adjustLoading.value = true
    await adjustStock(adjustPart.value.id, adjustForm)
    ElMessage.success('库存调整成功')
    showAdjustDialog.value = false
    loadParts()
  } catch (error) {
    console.error(error)
  } finally {
    adjustLoading.value = false
  }
}

const handleAddSubmit = async () => {
  try {
    await addFormRef.value.validate()
    addLoading.value = true
    await createPart(addForm)
    ElMessage.success('零件添加成功')
    showAddDialog.value = false
    Object.assign(addForm, {
      category: '',
      name: '',
      model_number: '',
      brand: '',
      unit_price: 0,
      stock_quantity: 0,
      min_stock: 5,
      location: '',
      compatible_models: ''
    })
    loadParts()
  } catch (error) {
    console.error(error)
  } finally {
    addLoading.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadParts()
})
</script>

<style scoped lang="scss">
:deep(.el-input-number) {
  .el-input__inner {
    height: 32px;
    line-height: 32px;
    font-size: 14px;
    color: #303133;
  }
  
  .el-input-number__decrease,
  .el-input-number__increase {
    width: 24px;
    font-size: 12px;
    
    .el-icon {
      font-size: 12px;
    }
  }
}
</style>
