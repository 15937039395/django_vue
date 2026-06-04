// Copyright (c) 2025 知识库管理系统. All rights reserved.

import request from '@/util/request'

/**
 * 获取知识库列表
 */
export function getRepositoryList(params) {
  return request.post('repository/search', params)
}

/**
 * 获取知识库详情
 */
export function getRepositoryDetail(id) {
  return request.get(`repository/detail?id=${id}`)
}

/**
 * 保存知识库
 */
export function saveRepository(data) {
  return request.post('repository/save', data)
}

/**
 * 更新知识库
 */
export function updateRepository(data) {
  return request.post('repository/save', data)
}

/**
 * 删除知识库
 */
export function deleteRepository(ids) {
  return request.del('repository/action', { ids })
}

/**
 * 点赞/取消点赞
 */
export function toggleLike(data) {
  return request.post('repository/like', data)
}

/**
 * 获取历史记录
 */
export function getHistoryList(repositoryId) {
  return request.get(`repository/history?id=${repositoryId}`)
}

/**
 * 获取评论列表
 */
export function getCommentList(repositoryId, page = 1, pageSize = 10, roleId = null, userId = null) {
  let url = `repository/comment/list?repository_id=${repositoryId}&page=${page}&page_size=${pageSize}`;
  if (roleId !== null) {
    url += `&role_id=${roleId}`;
  }
  if (userId !== null) {
    url += `&user_id=${userId}`;
  }
  return request.get(url);
}

/**
 * 提交评论
 */
export function submitComment(data) {
  return request.post('repository/comment/submit', data)
}

/**
 * 上传图片
 */
export function uploadImage(data) {
  return request.fileUpload('repository/upload/image', data)
}

// 复盘功能 API
/**
 * 获取复盘列表
 */
export function getReviewList(repositoryId, page = 1, pageSize = 10) {
  return request.get(`repository/review/list?id=${repositoryId}&page=${page}&page_size=${pageSize}`)
}

/**
 * 保存复盘
 */
export function saveReview(data) {
  return request.post('repository/review/save', data)
}

/**
 * 更新复盘
 */
export function updateReview(data) {
  return request.post('repository/review/update', data)
}

/**
 * 获取复盘详情
 */
export function getReviewDetail(reviewId) {
  return request.get(`repository/review/detail?id=${reviewId}`)
}

/**
 * 删除复盘
 */
export function deleteReview(data) {
  return request.post('repository/review/delete', data)
}