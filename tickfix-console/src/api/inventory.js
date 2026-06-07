import request from '@/utils/request'

export function getPartCategories() {
  return request({
    url: '/inventory/categories/',
    method: 'get'
  })
}

export function getParts(params) {
  return request({
    url: '/inventory/parts/',
    method: 'get',
    params
  })
}

export function getPart(id) {
  return request({
    url: `/inventory/parts/${id}/`,
    method: 'get'
  })
}

export function createPart(data) {
  return request({
    url: '/inventory/parts/',
    method: 'post',
    data
  })
}

export function updatePart(id, data) {
  return request({
    url: `/inventory/parts/${id}/`,
    method: 'put',
    data
  })
}

export function deletePart(id) {
  return request({
    url: `/inventory/parts/${id}/`,
    method: 'delete'
  })
}

export function adjustStock(id, data) {
  return request({
    url: `/inventory/parts/${id}/adjust_stock/`,
    method: 'post',
    data
  })
}

export function getLowStockParts() {
  return request({
    url: '/inventory/parts/low_stock/',
    method: 'get'
  })
}

export function getStockRecords(params) {
  return request({
    url: '/inventory/stock-records/',
    method: 'get',
    params
  })
}
