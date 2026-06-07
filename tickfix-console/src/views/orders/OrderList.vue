<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">接件单管理</h2>
      <el-button type="primary" @click="$router.push('/orders/create')">
        <el-icon><Plus /></el-icon>新建接件单
      </el-button>
    </div>

    <div class="card-wrapper">
      <div class="filter-bar">
        <el-input
          v-model="filters.search"
          placeholder="搜索单号/品牌/客户/取件码"
          clearable
          style="width: 280px"
          @keyup.enter="loadOrders"
        />
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 160px">
          <el-option
            v-for="item in statusOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-select v-model="filters.watch_type" placeholder="钟表类型" clearable style="width: 160px">
          <el-option
            v-for="item in watchTypeOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-button type="primary" @click="loadOrders">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>

      <el-table :data="orders" v-loading="loading" border>
        <el-table-column prop="order_no" label="接件单号" width="160" />
        <el-table-column label="钟表信息" min-width="180">
          <template #default="{ row }">
            <div>{{ row.brand }} {{ row.model }}</div>
            <div style="font-size: 12px; color: #909399">{{ row.watch_type_display }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="customer_name" label="客户姓名" width="100" />
        <el-table-column prop="customer_phone" label="客户电话" width="130" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="费用" width="120">
          <template #default="{ row }">
            <div>预估: ¥{{ row.estimated_cost }}</div>
            <div style="font-size: 12px; color: #909399">最终: ¥{{ row.final_cost }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="pickup_code" label="取件码" width="100">
          <template #default="{ row }">
            <el-tag type="info">{{ row.pickup_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="接件时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row.id)">详情</el-button>
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
          @size-change="loadOrders"
          @current-change="loadOrders"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getRepairOrders } from '@/api/repair'
import dayjs from 'dayjs'

const router = useRouter()

const statusOptions = [
  { value: 'pending', label: '待检测' },
  { value: 'inspecting', label: '检测中' },
  { value: 'quoted', label: '已报价待确认' },
  { value: 'customer_approved', label: '客户同意' },
  { value: 'customer_rejected', label: '客户拒绝' },
  { value: 'repairing', label: '维修中' },
  { value: 'parts_out', label: '零件出库' },
  { value: 'repaired', label: '维修完成' },
  { value: 'ready_for_pickup', label: '待取件' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

const watchTypeOptions = [
  { value: 'mechanical', label: '机械表' },
  { value: 'quartz', label: '石英表' },
  { value: 'wall', label: '挂钟' },
  { value: 'pocket', label: '怀表' },
  { value: 'other', label: '其他' }
]

const orders = ref([])
const loading = ref(false)

const filters = reactive({
  search: '',
  status: '',
  watch_type: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    inspecting: 'warning',
    quoted: 'warning',
    customer_approved: 'success',
    customer_rejected: 'danger',
    repairing: 'primary',
    parts_out: 'warning',
    repaired: 'success',
    ready_for_pickup: 'success',
    completed: 'success',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const viewDetail = (id) => {
  router.push(`/orders/${id}`)
}

const loadOrders = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    if (!params.search) delete params.search
    if (!params.status) delete params.status
    if (!params.watch_type) delete params.watch_type
    
    const data = await getRepairOrders(params)
    orders.value = data.results || []
    pagination.total = data.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.watch_type = ''
  pagination.page = 1
  loadOrders()
}

onMounted(() => {
  loadOrders()
})
</script>
