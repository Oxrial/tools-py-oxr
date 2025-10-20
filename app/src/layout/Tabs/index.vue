<!-- components/TabsView.vue -->
<template>
	<div class="tabs-container">
		<el-tabs
			v-model="activeTab"
			type="card"
			@tab-click="handleTabClick"
			@tab-remove="handleTabRemove"
			class="dynamic-tabs"
		>
			<el-tab-pane
				v-for="tab in tabs"
				:key="tab.id"
				:name="tab.id"
				:label="tab.title"
				:closable="tab.name !== 'HomeIndex'"
			>
				<!-- 标签页内容通过 router-view 渲染 -->
			</el-tab-pane>
		</el-tabs>
		<el-dropdown @command="handleDropdownCommand">
			<el-button text>
				<el-icon><More /></el-icon>
			</el-button>
			<template #dropdown>
				<el-dropdown-menu>
					<el-dropdown-item command="closeCurrent" :disabled="tabsStore.activeTab === 'HomeIndex'"
						>关闭当前</el-dropdown-item
					>
					<el-dropdown-item command="closeOther">关闭其他</el-dropdown-item>
					<el-dropdown-item command="closeAll" :disabled="tabsStore.activeTab === 'HomeIndex'"
						>关闭所有</el-dropdown-item
					>
				</el-dropdown-menu>
			</template>
		</el-dropdown>
	</div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTabsStore } from '@/store'
import type { CacheTab } from '@/store'
import { More, Refresh } from '@element-plus/icons-vue'
import type { TabsPaneContext } from 'element-plus'

const router = useRouter()
const route = useRoute()
const tabsStore = useTabsStore()

const tabs = computed<CacheTab[]>(() => tabsStore.tabs)
const activeTab = computed({
	get: (): string => tabsStore.activeTab,
	set: (value: string) => {
		tabsStore.activeTab = value
	}
})

// 刷新标签页
const refreshTab = (tabId: string) => {
	const tab = tabsStore.tabs.find((t) => t.id === tabId)
	if (!tab) return

	// 临时从缓存中移除组件，强制重新加载
	if (tab.cacheName) {
		tabsStore.cachedComponents.delete(tab.cacheName as string)

		// 延迟重新添加回缓存，确保组件重新创建
		setTimeout(() => {
			tabsStore.cachedComponents.add(tab.cacheName as string)

			// 重新导航到当前路由以触发组件重新加载
			if (tabId === route.fullPath) {
				router.replace({ path: '/redirect' + route.fullPath }).then(() => {
					router.replace(route.fullPath)
				})
			}
		}, 100)
	}
}
// 监听路由变化，更新激活的标签页
watch(
	() => route.fullPath,
	(newPath: string) => {
		const tab = tabsStore.tabs.find((tab) => tab.id === newPath)
		if (tab) {
			tabsStore.activeTab = newPath
		}
	},
	{ immediate: true }
)

// 点击标签页
const handleTabClick = (tab: TabsPaneContext): void => {
	const targetTab = tabsStore.tabs.find((t) => t.id === tab.paneName)
	if (targetTab && targetTab.fullPath !== route.fullPath) {
		router.push(targetTab.fullPath)
	}
}

// 关闭标签页
const handleTabRemove = (tabId: any): void => {
	tabsStore.closeTab(tabId as string, router)
}

// 下拉菜单命令类型
type DropdownCommand = 'refreshCurrent' | 'closeCurrent' | 'closeOther' | 'closeAll'

// 下拉菜单命令
const handleDropdownCommand = (command: DropdownCommand): void => {
	const currentTabId = tabsStore.activeTab

	switch (command) {
		case 'refreshCurrent':
			refreshTab(currentTabId)
			break
		case 'closeCurrent':
			handleTabRemove(currentTabId)
			break
		case 'closeOther':
			tabsStore.closeOtherTabs(currentTabId, router)
			break
		case 'closeAll':
			tabsStore.closeAllTabs(router)
			break
	}
}
</script>

<style scoped>
.tabs-container {
	display: flex;
	flex-direction: row;
	align-items: center;
}

.dynamic-tabs {
	flex: 1;
	display: flex;
	flex-direction: column;
}

:deep(.el-tabs__content) {
	display: none;
}

.tab-content {
	flex: 1;
	padding: 16px;
	overflow: auto;
}

:deep(.tab-label) {
	display: flex;
	align-items: center;
	gap: 8px;
}

:deep(.refresh-icon) {
	width: 12px;
	height: 12px;
	cursor: pointer;
	color: #909399;
	transition: color 0.3s;
}

:deep(.refresh-icon:hover) {
	color: #409eff;
}

.tab-component {
	height: 100%;
}
</style>
