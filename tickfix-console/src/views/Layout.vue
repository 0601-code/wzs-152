<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h2>TickFix</h2>
        <p>钟表维修管理</p>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <el-menu-item v-if="!route.meta?.hidden" :index="`/${route.path}`">
            <el-icon><component :is="route.meta.icon" /></el-icon>
            <span>{{ route.meta.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.userName }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessageBox, ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const menuRoutes = computed(() => {
  const layoutRoute = router.options.routes.find(r => r.path === '/')
  return layoutRoute?.children?.filter(r => !r.meta?.hidden) || []
})

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (err) {
      // 用户取消
    }
  }
}
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow: hidden;
  
  .logo {
    height: 60px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
    background-color: #2b2f3a;
    border-bottom: 1px solid #1f2d3d;
    
    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
    }
    
    p {
      margin: 2px 0 0 0;
      font-size: 12px;
      color: #909399;
    }
  }
  
  :deep(.el-menu) {
    border-right: none;
  }
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      color: #606266;
      
      &:hover {
        color: #409eff;
      }
    }
  }
}

.main-content {
  background-color: #f5f7fa;
  padding: 0;
  overflow-y: auto;
}
</style>
