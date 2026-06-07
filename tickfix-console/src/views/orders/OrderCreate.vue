<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">新建接件单</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>

    <div class="card-wrapper">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="钟表类型" prop="watch_type">
              <el-select v-model="form.watch_type" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="item in watchTypeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="品牌" prop="brand">
              <el-input v-model="form.brand" placeholder="请输入品牌" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="型号" prop="model">
              <el-input v-model="form.model" placeholder="请输入型号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="序列号">
              <el-input v-model="form.serial_number" placeholder="请输入序列号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="预估费用">
              <el-input-number v-model="form.estimated_cost" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">外观与故障</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="外观瑕疵">
              <el-input
                v-model="form.appearance_flaws"
                type="textarea"
                :rows="3"
                placeholder="请描述外观瑕疵情况"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="故障描述" prop="fault_description">
              <el-input
                v-model="form.fault_description"
                type="textarea"
                :rows="3"
                placeholder="请描述故障情况"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">客户信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="客户姓名" prop="customer_name">
              <el-input v-model="form.customer_name" placeholder="请输入客户姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="客户电话" prop="customer_phone">
              <el-input v-model="form.customer_phone" placeholder="请输入客户电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">提交接件</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createRepairOrder } from '@/api/repair'

const router = useRouter()

const watchTypeOptions = [
  { value: 'mechanical', label: '机械表' },
  { value: 'quartz', label: '石英表' },
  { value: 'wall', label: '挂钟' },
  { value: 'pocket', label: '怀表' },
  { value: 'other', label: '其他' }
]

const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  watch_type: '',
  brand: '',
  model: '',
  serial_number: '',
  appearance_flaws: '',
  fault_description: '',
  customer_name: '',
  customer_phone: '',
  estimated_cost: 0
})

const rules = {
  watch_type: [{ required: true, message: '请选择钟表类型', trigger: 'change' }],
  brand: [{ required: true, message: '请输入品牌', trigger: 'blur' }],
  fault_description: [{ required: true, message: '请输入故障描述', trigger: 'blur' }],
  customer_name: [{ required: true, message: '请输入客户姓名', trigger: 'blur' }],
  customer_phone: [{ required: true, message: '请输入客户电话', trigger: 'blur' }]
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    const data = await createRepairOrder(form)
    ElMessage.success('接件单创建成功')
    router.push(`/orders/${data.id}`)
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}
</script>
