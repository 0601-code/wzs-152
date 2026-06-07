import request from '@/utils/request'

export function getRepairOrders(params) {
  return request({
    url: '/repairs/orders/',
    method: 'get',
    params
  })
}

export function getRepairOrder(id) {
  return request({
    url: `/repairs/orders/${id}/`,
    method: 'get'
  })
}

export function createRepairOrder(data) {
  return request({
    url: '/repairs/orders/',
    method: 'post',
    data
  })
}

export function updateRepairOrder(id, data) {
  return request({
    url: `/repairs/orders/${id}/`,
    method: 'put',
    data
  })
}

export function transitionStatus(id, data) {
  return request({
    url: `/repairs/orders/${id}/transition/`,
    method: 'post',
    data
  })
}

export function addPartUsage(id, data) {
  return request({
    url: `/repairs/orders/${id}/add_part_usage/`,
    method: 'post',
    data
  })
}

export function getOrderByPickupCode(code) {
  return request({
    url: '/repairs/orders/by_pickup_code/',
    method: 'get',
    params: { code }
  })
}

export function getDashboardStats() {
  return request({
    url: '/repairs/orders/dashboard_stats/',
    method: 'get'
  })
}

export function getServiceItems(params) {
  return request({
    url: '/repairs/service-items/',
    method: 'get',
    params
  })
}

export function getStatusHistory(orderId) {
  return request({
    url: '/repairs/status-history/',
    method: 'get',
    params: { order: orderId }
  })
}
