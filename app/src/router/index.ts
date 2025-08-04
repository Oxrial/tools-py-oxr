import { createRouter, createWebHistory } from 'vue-router'
import type {
	NavigationGuardNext,
	RouteLocationNormalized,
	RouteLocationNormalizedLoaded,
	RouteRecordRaw
} from 'vue-router'
import Layout from '@/layout/index.vue'
import { capitalize } from 'lodash-es'
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
		meta: { title: '首页', icon: 'el-icon-house' },
		children: [
			{
				path: 'index',
				component: () => import('@/view/home/index.vue')
			}
		]
	},
	{
		path: '/config',
		component: Layout,
		redirect: '/config/index',
		meta: { title: '配置', icon: 'el-icon-operation', type: 'sub' },
		children: [
			{
				path: 'index',
				component: () => import('@/view/config/index.vue'),
				meta: { title: '配置', icon: 'el-icon-operation' }
			}
		]
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
	history: createWebHistory(import.meta.env.BASE_URL),
	routes
})
router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalizedLoaded, next: NavigationGuardNext) => {
	const name = to.fullPath.replace('//g', '').toUpperCase()
	// window name与路由匹配
	window.name = name
	next()
})
export default router
