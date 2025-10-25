import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'
import type {
	NavigationGuardNext,
	RouteLocationNormalized,
	RouteLocationNormalizedLoaded,
	RouteRecordRaw
} from 'vue-router'
import Layout from '@/layout/index.vue'
import { capitalize } from 'lodash-es'
import { useTabsStore } from '@/store'
export const routes: Array<RouteRecordRaw> = [
	{
		path: '/',
		redirect: '/home',
		meta: { notLayout: true }
	},
	{
		path: '/:pathMatch(.*)',
		redirect: '/404',
		meta: { notLayout: true }
	},
	{
		path: '/404',
		name: '404',
		component: () => import('@/view/error.vue'),
		meta: { notLayout: true }
	},
	{
		path: '/home',
		component: Layout,
		redirect: '/home/index',
		meta: { title: '首页 - 批量合并', icon: 'el-icon-house' },
		children: [
			{
				path: 'index',
				component: () => import('@/view/home/index.vue')
			}
		]
	},
	{
		path: '/convert',
		component: Layout,
		redirect: '/convert/index',
		meta: { title: '文件转换', icon: 'el-icon-switch' },
		children: [
			{
				path: 'index',
				component: () => import('@/view/convert/index.vue')
			}
		]
	},
	{
		path: '/config',
		component: Layout,
		redirect: '/config/index',
		meta: { title: '配置', icon: 'el-icon-operation' },
		children: [
			{
				path: 'index',
				component: () => import('@/view/config/index.vue')
			}
		]
	},
	{
		path: '/redirect/:path(.*)',
		meta: {
			notLayout: true,
			keepAlive: false // 重定向页面不需要缓存
		},
		component: () => import('@/view/Redirect.vue')
	}
]
const recursionRoutesArr = (routesArrTemp: Array<RouteRecordRaw>, parentsPath: string = '') => {
	routesArrTemp.forEach((item: RouteRecordRaw) => {
		if (!item.meta?.notLayout) {
			item.name =
				capitalize(parentsPath.substring(parentsPath.indexOf('/') + 1)) +
				capitalize(item.path.substring(item.path.indexOf('/') + 1))
			if (item.children) {
				recursionRoutesArr(item.children, item.path)
			}
		}
	})
}
recursionRoutesArr(routes)

const router = createRouter({
	history: createWebHashHistory(import.meta.env.BASE_URL),
	routes
})
// 路由守卫 - 添加标签页
router.beforeEach((to, from, next) => {
	const tabsStore = useTabsStore()

	// 跳过重定向路由
	if (to.name === 'Redirect') {
		next()
		return
	}

	// 只有有名称的路由才添加到标签页
	if (to.name) {
		tabsStore.addTab({
			name: to.name,
			path: to.path,
			meta: to.meta,
			fullPath: to.fullPath
		})
	}

	next()
})
export default router
