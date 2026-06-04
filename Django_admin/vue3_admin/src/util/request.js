// Copyright (c) 2025 知识库管理系统. All rights reserved.


// 引入axios
import axios from 'axios';
import router from '@/router';

let baseUrl = process.env.NODE_ENV === 'production' ? "http://139.224.62.106:8000/" : "/";
// 创建axios实例
const httpService = axios.create({
    baseURL: baseUrl,
    timeout: 1000000 // 需自定义
});

// 添加请求拦截器
import { touch } from '@/util/auth'; // 引入认证管理器的touch方法

httpService.interceptors.request.use(
    function (config) {
        // 更新最后活动时间
        touch();
        
        const token = window.sessionStorage.getItem('token');
        if (token) {
            config.headers.Authorization = 'Bearer ' + token; // 添加 Bearer 前缀以匹配后端期望
        }
        return config;
    },
    function (error) {
        return Promise.reject(error);
    }
);

// 添加响应拦截器
httpService.interceptors.response.use(
    function (response) {
        return response;
    },
    function (error) {
        // 统一处理需要跳转到登录页的错误状态码
        if (error.response?.status === 401 || error.response?.status === 500) {
            // 清理本地存储的认证信息
            window.sessionStorage.removeItem("token");
            // 跳转到登录页面
            router.push("/login").catch(err => {
                console.warn('路由跳转失败:', err);
            });
        }
        return Promise.reject(error);
    }
);

/* 网络请求部分 */

export function get(url, params = {}, config = {}) {
    return httpService({ url, method: 'get', params, ...config });
}

export function post(url, params = {}) {
    return httpService({ url, method: 'post', data: params });
}

export function del(url, params = {}) {
    return httpService({ url, method: 'delete', data: params });
}

// 添加delete别名，与del方法功能相同
export function deleteRequest(url, params = {}) {
    return httpService({ url, method: 'delete', data: params });
}

export function fileUpload(url, params = new FormData()) {
    return httpService({
        url,
        method: 'post',
        data: params,
        headers: { 'Content-Type': 'multipart/form-data' }
    });
}

export function getServerUrl() {
    return baseUrl;
}

export default {
    get,
    post,
    del,
    delete: deleteRequest,
    fileUpload,
    getServerUrl
};