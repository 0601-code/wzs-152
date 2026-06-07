import { defineStore } from 'pinia'
import { login, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    refreshToken: localStorage.getItem('refresh_token') || '',
    userInfo: JSON.parse(localStorage.getItem('user_info') || 'null')
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    userRole: (state) => state.userInfo?.role || '',
    userName: (state) => state.userInfo?.username || ''
  },

  actions: {
    async login(credentials) {
      const response = await login(credentials)
      this.token = response.access
      this.refreshToken = response.refresh
      this.userInfo = response.user
      
      localStorage.setItem('access_token', response.access)
      localStorage.setItem('refresh_token', response.refresh)
      localStorage.setItem('user_info', JSON.stringify(response.user))
      
      return response
    },

    async fetchUserInfo() {
      const userInfo = await getUserInfo()
      this.userInfo = userInfo
      localStorage.setItem('user_info', JSON.stringify(userInfo))
      return userInfo
    },

    logout() {
      this.token = ''
      this.refreshToken = ''
      this.userInfo = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
    }
  }
})
