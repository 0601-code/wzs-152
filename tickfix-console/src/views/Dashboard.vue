<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">工作台</h2>
    </div>

    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total || 0 }}</div>
              <div class="stat-label">总接件单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending || 0 }}</div>
              <div class="stat-label">待检测</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon repairing">
              <el-icon><Tools /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.repairing || 0 }}</div>
              <div class="stat-label">维修中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon ready">
              <el-icon><Present /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.ready_for_pickup || 0 }}</div>
              <div class="stat-label">待取件</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-cards">
      <el-col :span="16">
        <el-card class="list-card">
          <template #header>
            <div class="card-header">
              <span>最近接件单</span>
              <el-button type="primary" link @click="$router.push('/orders')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentOrders" v-loading="loading">
            <el-table-column prop="order_no" label="单号" width="160" />
            <el-table-column prop="brand" label="品牌" width="100" />
            <el-table-column prop="model" label="型号" width="120" />
            <el-table-column prop="customer_name" label="客户" width="100" />
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="接件时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" link @click="viewOrder(row.id)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="list-card">
          <template #header>
            <div class="card-header">
              <span>库存预警</span>
            </div>
          </template>
          <el-table :data="lowStockParts" v-loading="partsLoading">
            <el-table-column prop="name" label="零件名称" />
            <el-table-column prop="model_number" label="型号" width="120" />
            <el-table-column label="库存" width="80">
              <template #default="{ row }">
                <el-tag type="danger">{{ row.stock_quantity }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardStats, getRepairOrders } from '@/api/repair'
import { getLowStockParts } from '@/api/inventory'
import dayjs from 'dayjs'

const router = useRouter()

const stats = ref({})
const recentOrders = ref([])
const lowStockParts = ref([])
const loading = ref(false)
const partsLoading = ref(false)

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

const viewOrder = (id) => {
  router.push(`/orders/${id}`)
}

const loadData = async () => {
  try {
    loading.value = true
    partsLoading.value = true
    const [statsData, ordersData, partsData] = await Promise.all([
      getDashboardStats(),
      getRepairOrders({ page_size: 8 }),
      getLowStockParts()
    ])
    stats.value = statsData
    recentOrders.value = ordersData.results || []
    lowStockParts.value = partsData
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
    partsLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  .stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: #fff;
    
    &.total { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    &.pending { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    &.repairing { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    &.ready { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
  }
  
  .stat-info {
    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: #303133;
    }
    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-top: 4px;
    }
  }
}

.content-cards {
  .list-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
    }
  }
}
</style>
