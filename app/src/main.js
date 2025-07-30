import { createApp } from 'vue'
import App from './App.vue'
import 'normalize.css/normalize.css'
import 'element-plus/theme-chalk/index.css' // if you just want to import css
import 'element-plus/theme-chalk/dark/css-vars.css'
import { createPinia } from 'pinia'

import store from '@/store'
const pinia = createPinia()
pinia.use(store)

const app = createApp(App)
app.use(pinia)
app.mount('#app')
