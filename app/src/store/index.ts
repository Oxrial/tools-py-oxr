import { defineStore } from 'pinia'
import { useDark, useToggle } from '@vueuse/core'
import type { Router } from 'vue-router'

export const useDarkModeStore = defineStore('darkMode', () => {
	const isDark = useDark({
		// 默认值
		initialValue: 'dark',
		storageKey: 'DARK_MODE',
		// 暗黑class名字
		valueDark: 'dark',
		// 高亮class名字
		valueLight: 'light',
		listenToStorageChanges: true,
		initOnMounted: true,
		mergeDefaults: true
	})
	const toggleDark = useToggle(isDark)
	return { isDark, toggleDark }
})

export interface CacheTab {
	id: string
	name: string | symbol | null | undefined
	path: string
	fullPath: string
	title: string
	cacheName: string | symbol | null | undefined
}
interface RouteMeta {
	title?: string
	keepAlive?: boolean
	[key: string]: any
}

interface TabRoute {
	name: string | symbol | null | undefined
	path: string
	meta: RouteMeta
	fullPath: string
}
export const useTabsStore = defineStore('tabs', () => {
	// 标签页列表
	const tabs = ref<Array<CacheTab>>([])
	// 当前激活的标签页
	const activeTab = ref<string>('')
	const cachedComponents = ref<Set<string>>(new Set())
	// 添加标签页
	const addTab = (route: TabRoute) => {
		const { name, path, meta, fullPath } = route
		const tabId = fullPath || path

		// 检查是否已存在
		const existingTab = tabs.value.find((tab) => tab.id === tabId)
		if (existingTab) {
			activeTab.value = tabId
			return
		}
		// 添加新标签页
		tabs.value.push({
			id: tabId,
			name: name || path,
			path: path,
			fullPath: fullPath,
			title: meta?.title || (name as string) || '未命名',
			cacheName: name // 用于 keep-alive 的缓存标识
		})
		// 添加到缓存集合
		if (meta?.keepAlive !== false) {
			cachedComponents.value.add(name as string)
		}
		activeTab.value = tabId
	}

	// 关闭标签页
	const closeTab = (tabId: string, router: Router) => {
		console.log(tabId)
		const index = tabs.value.findIndex((tab) => tab.id === tabId)
		if (index === -1) return

		const tab = tabs.value[index]
		tabs.value.splice(index, 1)
		// 从缓存中移除
		if (tab.cacheName) {
			cachedComponents.value.delete(tab.cacheName as string)
		}
		tabs.value.splice(index, 1)
		// 如果关闭的是当前激活的标签页，需要激活另一个标签页
		if (activeTab.value === tabId) {
			if (tabs.value.length > 0) {
				const newActiveTab = tabs.value[Math.max(0, index - 1)]
				activeTab.value = newActiveTab.id
				router.push(newActiveTab.fullPath)
			} else {
				activeTab.value = ''
				router.push('/')
			}
		}
	}

	// 关闭其他标签页
	const closeOtherTabs = (tabId: string, router: Router) => {
		const tabToKeep = tabs.value.find((tab) => tab.id === tabId)
		if (!tabToKeep) return
		const tabsToKeep = tabs.value.filter((tab) => tab.id === tabId || tab.name === 'HomeIndex')

		tabs.value.forEach((tab) => {
			if (tab.id !== tabId && tab.name !== 'HomeIndex' && tab.cacheName) {
				cachedComponents.value.delete(tab.cacheName as string)
			}
		})
		tabs.value = tabsToKeep
		activeTab.value = tabId
		router.push(tabToKeep.fullPath)
	}

	// 关闭所有标签页
	const closeAllTabs = (router: Router) => {
		const homeTab = tabs.value.find((tab) => tab.name === 'HomeIndex')

		// 清空所有缓存
		cachedComponents.value.clear()
		if (homeTab && homeTab.cacheName) {
			cachedComponents.value.add(homeTab.cacheName as string)
			// 只保留 HomeIndex 标签
			tabs.value = [homeTab]
			activeTab.value = homeTab.id
			router.push(homeTab.fullPath)
		} else {
			// 若没有 HomeIndex，则全部清空
			tabs.value = []
			activeTab.value = ''
			router.push('/')
		}
	}
	// 获取缓存的组件名称数组（用于 keep-alive）
	const getCachedComponents = computed(() => {
		return Array.from(cachedComponents.value)
	})
	return {
		tabs,
		activeTab,
		cachedComponents,
		getCachedComponents,
		addTab,
		closeTab,
		closeOtherTabs,
		closeAllTabs
	}
})
