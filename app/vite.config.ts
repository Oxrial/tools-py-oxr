import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import vueJsx from '@vitejs/plugin-vue-jsx'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import http from 'http'
import setupExtend from 'vite-plugin-vue-setup-extend'

// https://vitejs.dev/config/
export default defineConfig(() => ({
	base: './',
	server: {
		port: 39000,
		strictPort: true,
		host: true,
		proxy: {
			// 代理拦截匹配前缀
			'/api': {
				target: 'http://127.0.0.1:39001',
				changeOrigin: true,
				agent: new http.Agent(),
				rewrite: (path) => path.replace(/^\/api/, ''),
				configure: (proxy) => {
					proxy.on('error', (err: any, _, res) => {
						console.error('Proxy error:', err)
						if (err.code === 'ECONNREFUSED') {
							res.writeHead(404, { 'Content-Type': 'application/json' })
							res.end('服务未启动')
						} else {
							res.writeHead(500, { 'Content-Type': 'application/json' })
							res.end('代理错误')
						}
					})
				}
			}
		}
	},
	resolve: {
		alias: {
			'@': resolve(__dirname, './src')
		}
	},
	plugins: [
		vue(),
		vueJsx(),
		AutoImport({
			imports: ['vue', 'vue-router', 'pinia'],
			dts: 'src/types/auto-import.d.ts',
			resolvers: [ElementPlusResolver()]
		}),
		Components({
			include: [/\.vue$/, /\.vue\?vue/, /\?vue/, /\.tsx$/],
			dts: 'src/types/components.d.ts',
			resolvers: [ElementPlusResolver()]
		}),
		setupExtend()
	],
	css: {
		preprocessorOptions: {
			scss: {
				additionalData: `
					@use "@/layout/theme/variable.scss" as *;`,
				silenceDeprecations: ['legacy-js-api']
			}
		}
	},
	clearScreen: false,
	build: {
		outDir: '../dist',
		emptyOutDir: true,
		/** 单个 chunk 文件的大小超过 2048KB 时发出警告 */
		chunkSizeWarningLimit: 2048,
		/** 禁用 gzip 压缩大小报告 */
		reportCompressedSize: false,
		/** 打包后静态资源目录 */
		assetsDir: 'static',
		rollupOptions: {
			output: {
				manualChunks: {
					vue: ['vue', 'vue-router', 'pinia'],
					element: ['element-plus', '@element-plus/icons-vue']
				}
			}
		}
	}
}))
