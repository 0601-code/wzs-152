<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">取件查询</h2>
    </div>

    <div class="card-wrapper" style="max-width: 600px; margin: 0 auto;">
      <el-form :inline="true" @submit.prevent="searchOrder">
        <el-form-item label="取件码">
          <el-input
            v-model="pickupCode"
            placeholder="请输入6位取件码"
            maxlength="6"
            size="large"
            style="width: 300px"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="searchOrder">
            查询
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="order" class="order-result">
        <el-descriptions :column="1" border title="取件信息">
          <el-descriptions-item label="接件单号">
            {{ order.order_no }}
          </el-descriptions-item>
          <el-descriptions-item label="钟表信息">
            {{ order.brand }} {{ order.model }}
          </el-descriptions-item>
          <el-descriptions-item label="客户姓名">
            {{ order.customer_name }}
          </el-descriptions-item>
          <el-descriptions-item label="客户电话">
            {{ order.customer_phone }}
          </el-descriptions-item>
          <el-descriptions-item label="维修状态">
            <el-tag :type="getStatusType(order.status)" size="large">
              {{ order.status_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="接件时间">
            {{ formatDate(order.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最终费用" v-if="order.status === 'ready_for_pickup' || order.status === 'completed'">
            <span style="font-size: 20px; font-weight: 700; color: #f56c6c">
              ¥{{ order.final_cost }}
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="action-bar" v-if="order.status === 'ready_for_pickup'">
          <el-button type="success" size="large" @click="handlePickup">
            确认取件结算
          </el-button>
        </div>
      </div>

      <el-empty v-else-if="searched && !order" description="未找到对应接件单，请核对取件码" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrderByPickupCode, transitionStatus } from '@/api/repair'
import dayjs from 'dayjs'

const pickupCode = ref('')
const order = ref(null)
const loading = ref(false)
const searched = ref(false)

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

const searchOrder = async () => {
  if (!pickupCode.value.trim()) {
    ElMessage.warning('请输入取件码')
    return
  }
  try {
    loading.value = true
    searched.value = true
    order.value = await getOrderByPickupCode(pickupCode.value.trim())
  } catch (error) {
    order.value = null
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handlePickup = async () => {
  try {
    await ElMessageBox.confirm(
      `确认客户 ${order.value.customer_name} 取件？最终费用 ¥${order.value.final_cost}`,
      '取件确认',
      {
        confirmButtonText: '确认取件',
        cancelButtonText: '取消',
        type: 'success'
      }
    )
    await transitionStatus(order.value.id, {
      new_status: 'completed',
      remark: '客户取件完成'
    })
    ElMessage.success('取件完成')
    searchOrder()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}
</script>

<style scoped lang="scss">
.order-result {
  margin-top: 30px;
  
  .action-bar {
    margin-top: 20px;
    text-align: center;
  }
}
</style>
