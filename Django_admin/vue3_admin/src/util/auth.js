// Copyright (c) 2025 知识库管理系统. All rights reserved.

/**
 * 用户认证和会话管理工具
 */
class AuthManager {
  // 会话超时时间（2小时 = 7200000毫秒）
  static TIMEOUT_DURATION = 2 * 60 * 60 * 1000;

  constructor() {
    this.lastActivityTime = this.getLastActivityTime();
    this.timeoutTimer = null;
    this.startMonitoring();
  }

  /**
   * 获取最后活动时间
   */
  getLastActivityTime() {
    const storedTime = window.sessionStorage.getItem('lastActivityTime');
    return storedTime ? parseInt(storedTime, 10) : Date.now();
  }

  /**
   * 更新最后活动时间
   */
  updateLastActivityTime() {
    const now = Date.now();
    this.lastActivityTime = now;
    window.sessionStorage.setItem('lastActivityTime', now.toString());
  }

  /**
   * 检查会话是否超时
   */
  isSessionExpired() {
    const now = Date.now();
    const timeDiff = now - this.lastActivityTime;
    return timeDiff > AuthManager.TIMEOUT_DURATION;
  }

  /**
   * 重置超时计时器
   */
  resetTimeout() {
    if (this.timeoutTimer) {
      clearTimeout(this.timeoutTimer);
    }

    // 如果会话已过期，则立即跳转
    if (this.isSessionExpired()) {
      this.handleSessionTimeout();
      return;
    }

    // 设置新的超时计时器
    this.timeoutTimer = setTimeout(() => {
      this.handleSessionTimeout();
    }, AuthManager.TIMEOUT_DURATION - (Date.now() - this.lastActivityTime));
  }

  /**
   * 处理会话超时
   */
  handleSessionTimeout() {
    console.log('会话超时，正在跳转到登录页面...');
    
    // 清理认证信息
    window.sessionStorage.removeItem('token');
    window.sessionStorage.removeItem('currentUser');
    window.sessionStorage.removeItem('menuList');
    window.sessionStorage.removeItem('lastActivityTime');
    
    // 跳转到登录页面
    window.location.href = '/#/login';
    window.location.reload();
  }

  /**
   * 开始监控用户活动
   */
  startMonitoring() {
    // 监听用户活动事件
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click', 'wheel'].forEach(eventType => {
      document.addEventListener(eventType, () => {
        this.onUserActivity();
      }, { passive: true });
    });

    // 定期检查会话状态
    setInterval(() => {
      if (this.isSessionExpired()) {
        this.handleSessionTimeout();
      }
    }, 60000); // 每分钟检查一次

    // 初始化超时计时器
    this.resetTimeout();
  }

  /**
   * 用户活动回调
   */
  onUserActivity() {
    this.updateLastActivityTime();
    this.resetTimeout();
  }

  /**
   * 手动触发活动更新
   */
  touch() {
    this.onUserActivity();
  }

  /**
   * 获取剩余时间（毫秒）
   */
  getTimeRemaining() {
    const now = Date.now();
    const timeDiff = now - this.lastActivityTime;
    return Math.max(0, AuthManager.TIMEOUT_DURATION - timeDiff);
  }

  /**
   * 获取剩余时间（格式化为 HH:MM:SS）
   */
  getTimeRemainingFormatted() {
    const remaining = this.getTimeRemaining();
    const hours = Math.floor(remaining / (1000 * 60 * 60));
    const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((remaining % (1000 * 60)) / 1000);
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }
}

// 创建全局实例
const authManager = new AuthManager();

// 导出实例和工具函数
export default authManager;

// 导出工具函数
export const isSessionExpired = authManager.isSessionExpired.bind(authManager);
export const getTimeRemaining = authManager.getTimeRemaining.bind(authManager);
export const getTimeRemainingFormatted = authManager.getTimeRemainingFormatted.bind(authManager);
export const touch = authManager.touch.bind(authManager);