<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">接件单详情</h2>
      <div>
        <el-button @click="$router.back()">返回列表</el-button>
        <el-dropdown v-if="order && order.next_statuses && order.next_statuses.length > 0" @command="handleStatusChange">
          <el-button type="primary">
            状态流转
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="status in order.next_statuses"
                :key="status.value"
                :command="status.value"
              >
                {{ status.label }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div v-loading="loading" class="detail-container">
      <template v-if="order">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <span>基本信息</span>
                  <el-tag :type="getStatusType(order.status)" size="large">
                    {{ order.status_display }}
                  </el-tag>
                </div>
              </template>
              <el-descriptions :column="3" border>
                <el-descriptions-item label="接件单号">{{ order.order_no }}</el-descriptions-item>
                <el-descriptions-item label="取件码">
                  <el-tag type="info" size="large">{{ order.pickup_code }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="钟表类型">{{ order.watch_type_display }}</el-descriptions-item>
                <el-descriptions-item label="品牌">{{ order.brand }}</el-descriptions-item>
                <el-descriptions-item label="型号">{{ order.model }}</el-descriptions-item>
                <el-descriptions-item label="序列号">{{ order.serial_number || '-' }}</el-descriptions-item>
                <el-descriptions-item label="客户姓名">{{ order.customer_name }}</el-descriptions-item>
                <el-descriptions-item label="客户电话">{{ order.customer_phone }}</el-descriptions-item>
                <el-descriptions-item label="接件时间">{{ formatDate(order.created_at) }}</el-descriptions-item>
                <el-descriptions-item label="接件人">{{ order.created_by_info?.username || '-' }}</el-descriptions-item>
                <el-descriptions-item label="维修技师">{{ order.technician_info?.username || '-' }}</el-descriptions-item>
              </el-descriptions>
            </el-card>

            <el-card class="info-card">
              <template #header>
                <span>外观与故障</span>
              </template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="外观瑕疵">
                  {{ order.appearance_flaws || '无' }}
                </el-descriptions-item>
                <el-descriptions-item label="故障描述">
                  {{ order.fault_description }}
                </el-descriptions-item>
                <el-descriptions-item label="检测报告" v-if="order.inspection_report">
                  {{ order.inspection_report }}
                </el-descriptions-item>
                <el-descriptions-item label="报价说明" v-if="order.quote_remark">
                  {{ order.quote_remark }}
                </el-descriptions-item>
                <el-descriptions-item label="维修备注" v-if="order.repair_remark">
                  {{ order.repair_remark }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>

            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <span>零件消耗记录</span>
                  <el-button
                    v-if="canAddPart"
                    type="primary"
                    size="small"
                    @click="showPartDialog = true"
                  >
                    添加零件
                  </el-button>
                  <el-tooltip v-else content="当前状态不允许添加零件">
                    <el-button type="primary" size="small" disabled>
                      添加零件
                    </el-button>
                  </el-tooltip>
                </div>
              </template>
              <el-table :data="order.part_usages || []" size="small">
                <el-table-column prop="part_info.name" label="零件名称" />
                <el-table-column prop="part_info.model_number" label="型号" width="140" />
                <el-table-column prop="quantity" label="数量" width="80" />
                <el-table-column prop="unit_price" label="单价" width="100">
                  <template #default="{ row }">¥{{ row.unit_price }}</template>
                </el-table-column>
                <el-table-column label="小计" width="100">
                  <template #default="{ row }">¥{{ (row.quantity * row.unit_price).toFixed(2) }}</template>
                </el-table-column>
                <el-table-column prop="operator_name" label="操作人" width="100" />
                <el-table-column prop="out_at" label="出库时间" width="160">
                  <template #default="{ row }">{{ formatDate(row.out_at) }}</template>
                </el-table-column>
              </el-table>
            </el-card>

            <el-card class="info-card">
              <template #header>
                <span>状态流转记录</span>
              </template>
              <el-timeline>
                <el-timeline-item
                  v-for="item in order.status_history || []"
                  :key="item.id"
                  :timestamp="formatDate(item.created_at)"
                  placement="top"
                >
                  <el-tag :type="getStatusType(item.to_status)">
                    {{ item.to_status_display }}
                  </el-tag>
                  <span style="margin-left: 12px; color: #606266">
                    操作人: {{ item.operator_name || '-' }}
                  </span>
                  <p v-if="item.remark" style="margin-top: 8px; color: #909399; font-size: 12px">
                    备注: {{ item.remark }}
                  </p>
                </el-timeline-item>
              </el-timeline>
            </el-card>
          </el-col>

          <el-col :span="8">
            <el-card class="info-card">
              <template #header>
                <span>费用信息</span>
              </template>
              <div class="fee-item">
                <span class="fee-label">预估费用</span>
                <span class="fee-value">¥{{ order.estimated_cost }}</span>
              </div>
              <div class="fee-item">
                <span class="fee-label">零件费用</span>
                <span class="fee-value">¥{{ order.parts_cost }}</span>
              </div>
              <div class="fee-item">
                <span class="fee-label">工时费用</span>
                <span class="fee-value">¥{{ order.labor_cost }}</span>
              </div>
              <el-divider />
              <div class="fee-item total">
                <span class="fee-label">最终费用</span>
                <span class="fee-value">¥{{ order.final_cost }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </template>
    </div>

    <el-dialog v-model="showStatusDialog" title="状态流转" width="500px">
      <el-form :model="statusForm" label-width="100px">
        <el-form-item label="目标状态">
          <el-tag :type="getStatusType(statusForm.new_status)">
            {{ getStatusLabel(statusForm.new_status) }}
          </el-tag>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="statusForm.remark" type="textarea" :rows="3" />
        </el-form-item>
        <template v-if="statusForm.new_status === 'quoted'">
          <el-form-item label="检测报告">
            <el-input v-model="statusForm.inspection_report" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="报价说明">
            <el-input v-model="statusForm.quote_remark" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item label="预估费用">
            <el-input-number v-model="statusForm.estimated_cost" :min="0" :precision="2" />
          </el-form-item>
        </template>
        <template v-if="['customer_approved', 'repairing'].includes(statusForm.new_status)">
          <el-form-item label="工时费用">
            <el-input-number v-model="statusForm.labor_cost" :min="0" :precision="2" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showStatusDialog = false">取消</el-button>
        <el-button type="primary" :loading="statusLoading" @click="confirmStatusChange">确认</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPartDialog" title="添加零件" width="600px">
      <el-form :model="partForm" label-width="100px">
        <el-form-item label="选择零件" prop="part_id">
          <el-select
            v-model="partForm.part_id"
            filterable
            placeholder="搜索并选择零件"
            style="width: 100%"
          >
            <el-option
              v-for="part in partsList"
              :key="part.id"
              :label="`${part.name} (${part.model_number}) - 库存:${part.stock_quantity}`"
              :value="part.id"
              :disabled="part.stock_quantity <= 0"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="partForm.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="partForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPartDialog = false">取消</el-button>
        <el-button type="primary" :loading="partLoading" @click="confirmAddPart">确认出库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRepairOrder, transitionStatus, addPartUsage } from '@/api/repair'
import { getParts } from '@/api/inventory'
import dayjs from 'dayjs'

const route = useRoute()
const orderId = computed(() => route.params.id)

const order = ref(null)
const loading = ref(false)
const showStatusDialog = ref(false)
const showPartDialog = ref(false)
const statusLoading = ref(false)
const partLoading = ref(false)
const partsList = ref([])

const statusForm = reactive({
  new_status: '',
  remark: '',
  inspection_report: '',
  quote_remark: '',
  estimated_cost: 0,
  labor_cost: 0
})

const partForm = reactive({
  part_id: null,
  quantity: 1,
  remark: ''
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

const canAddPart = computed(() => {
  if (!order.value) return false
  const allowed = ['customer_approved', 'repairing', 'parts_out']
  return allowed.includes(order.value.status)
})

const getStatusLabel = (status) => {
  const labelMap = {
    pending: '待检测',
    inspecting: '检测中',
    quoted: '已报价待确认',
    customer_approved: '客户同意',
    customer_rejected: '客户拒绝',
    repairing: '维修中',
    parts_out: '零件出库',
    repaired: '维修完成',
    ready_for_pickup: '待取件',
    completed: '已完成',
    cancelled: '已取消'
  }
  return labelMap[status] || status
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadOrder = async () => {
  try {
    loading.value = true
    order.value = await getRepairOrder(orderId.value)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadParts = async () => {
  try {
    const data = await getParts({ page_size: 100 })
    partsList.value = data.results || []
  } catch (error) {
    console.error(error)
  }
}

const handleStatusChange = (newStatus) => {
  statusForm.new_status = newStatus
  statusForm.remark = ''
  statusForm.inspection_report = order.value.inspection_report || ''
  statusForm.quote_remark = order.value.quote_remark || ''
  statusForm.estimated_cost = order.value.estimated_cost || 0
  statusForm.labor_cost = order.value.labor_cost || 0
  showStatusDialog.value = true
}

const confirmStatusChange = async () => {
  try {
    statusLoading.value = true
    await transitionStatus(orderId.value, statusForm)
    ElMessage.success('状态更新成功')
    showStatusDialog.value = false
    loadOrder()
  } catch (error) {
    console.error(error)
  } finally {
    statusLoading.value = false
  }
}

const confirmAddPart = async () => {
  if (!partForm.part_id) {
    ElMessage.warning('请选择零件')
    return
  }
  try {
    partLoading.value = true
    await addPartUsage(orderId.value, partForm)
    ElMessage.success('零件出库成功')
    showPartDialog.value = false
    partForm.part_id = null
    partForm.quantity = 1
    partForm.remark = ''
    loadOrder()
  } catch (error) {
    console.error(error)
  } finally {
    partLoading.value = false
  }
}

onMounted(() => {
  loadOrder()
  loadParts()
})
</script>

<style scoped lang="scss">
.info-card {
  margin-bottom: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.fee-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  
  .fee-label {
    color: #606266;
  }
  
  .fee-value {
    font-size: 16px;
    font-weight: 500;
  }
  
  &.total {
    .fee-label {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
    .fee-value {
      font-size: 24px;
      font-weight: 700;
      color: #f56c6c;
    }
  }
}
</style>
