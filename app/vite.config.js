import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
	plugins: [vue()],
	base: './', // 使用相对路径
	build: {
		outDir: '../dist', // 构建输出到上级dist目录
		emptyOutDir: true,
		rollupOptions: {
			output: {
				manualChunks: undefined, // 禁用代码分割，优化加载
				entryFileNames: `[name].js`,
				chunkFileNames: `[name].js`,
				assetFileNames: `[name].[ext]`
			}
		}
	}
})
