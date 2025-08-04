import { createApp } from 'vue'
import AppView from './App.vue'
import 'normalize.css/normalize.css'
import 'element-plus/theme-chalk/index.css' // if you just want to import css
import 'element-plus/theme-chalk/dark/css-vars.css'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import * as Icons from '@element-plus/icons-vue'
import { hump2Bar } from '@/util'
import router from './router'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const app = createApp(AppView)
// 使图标像普通svg图片使用，全局注册为组件形式
for (const icon in Icons) {
	app.component(`el-icon-${hump2Bar(icon)}`, (Icons as any)[icon])
}
app.use(pinia)
app.use(router).mount('#app')
