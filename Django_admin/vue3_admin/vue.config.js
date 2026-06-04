const webpack = require('webpack');

const path = require('path')
function resolve(dir) {
    return path.join(__dirname, dir)
}

module.exports = {
    lintOnSave: false,
    
    // 生产环境构建配置
    publicPath: './',  // 使用相对路径，适配任何域名
    outputDir: 'dist',  // 构建输出目录
    assetsDir: 'static',  // 静态资源目录
    
    // 配置 webpack 统计信息，过滤掉 Sass 弃用警告
    configureWebpack: {
        stats: {
            warningsFilter: [
                /Deprecation The legacy JS API is deprecated/,
                /sass-lang\.com\/d\/legacy-js-api/
            ]
        },
        resolve: {
            fallback: {
                "process/browser": require.resolve("process/browser")
            }
        },
        plugins: [
            new webpack.ProvidePlugin({
                process: 'process/browser',
            }),
        ]
    },

    devServer: {
        // 配置客户端覆盖层，过滤掉特定错误（仅开发环境）
        client: {
            overlay: {
                runtimeErrors: (error) => {
                    // 忽略的错误列表
                    const ignoreErrors = [
                        'crypto.randomUUID is not a function',  // 浏览器扩展
                        'chrome-extension://',                   // 浏览器扩展
                        'Script error.',                        // 高德地图内部错误
                        't.split is not a function',            // 高德地图内部错误
                    ];
                    
                    // 检查错误消息或堆栈是否包含忽略的关键字
                    const shouldIgnore = ignoreErrors.some(ignored => 
                        error.message?.includes(ignored) || 
                        error.stack?.includes(ignored)
                    );
                    
                    if (shouldIgnore) {
                        return false  // 不显示错误弹窗
                    }
                    return true  // 其他错误正常显示
                },
            },
        },
        proxy: {
            '/user': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/role': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/menu': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/level': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/post': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/department': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/post': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/ops': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/notification': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/repository': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/event': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/classify': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/items': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/blacklist': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/manhour': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/files': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/approval': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/log': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/media': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            }
        }
    },

    chainWebpack(config) {
        // 配置 sass-loader 忽略 legacy-js-api 弃用警告
        config.module
            .rule('scss')
            .oneOf('vue')
            .use('sass-loader')
            .tap(options => {
                return {
                    ...options,
                    sassOptions: {
                        silenceDeprecations: ['legacy-js-api']
                    }
                }
            })

        // 设置 svg-sprite-loader
        // config 为 webpack 配置对象
        // config.module 表示创建一个具名规则，以后用来修改规则
        config.module
            // 规则
            .rule('svg')
            // 忽略
            .exclude.add(resolve('src/icons'))
            // 结束
            .end()
        // config.module 表示创建一个具名规则，以后用来修改规则
        config.module
            // 规则
            .rule('icons')
            // 正则，解析 .svg 格式文件
            .test(/\.svg$/)
            // 解析的文件
            .include.add(resolve('src/icons'))
            // 结束
            .end()
            // 新增了一个解析的loader
            .use('svg-sprite-loader')
            // 具体的loader
            .loader('svg-sprite-loader')
            // loader 的配置
            .options({
                symbolId: 'icon-[name]'
            })
            // 结束
            .end()
        config
            .plugin('ignore')
            .use(
                new webpack.ContextReplacementPlugin(/moment[/\\]locale$/, /zh-cn$/)
            )
        config.module
            .rule('icons')
            .test(/\.svg$/)
            .include.add(resolve('src/icons'))
            .end()
            .use('svg-sprite-loader')
            .loader('svg-sprite-loader')
            .options({
                symbolId: 'icon-[name]'
            })
            .end()
    }
}
