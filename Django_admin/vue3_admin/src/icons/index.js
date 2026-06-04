// Copyright (c) 2025 知识库管理系统. All rights reserved.


import SvgIcon from '@/components/SvgIcon'

// 封装 SVG 图标注册逻辑
function registerSvgIcons() {
    try {
        const svgRequired = require.context('./svg', false, /\.svg$/)
        svgRequired.keys().forEach((item) => {
            try {
                svgRequired(item)
            } catch (iconError) {
                console.warn(`Failed to load SVG icon: ${item}`, iconError)
            }
        })
    } catch (contextError) {
        console.error('Failed to initialize SVG icons context', contextError)
    }
}

// 执行图标注册
registerSvgIcons()

export default (app) => {
    if (!app || typeof app.component !== 'function') {
        console.error('Invalid Vue app instance provided')
        return
    }

    app.component('svg-icon', SvgIcon)
}