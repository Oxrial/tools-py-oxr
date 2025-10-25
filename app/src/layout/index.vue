<template>
	<el-container>
		<el-aside width="auto">
			<div class="aside-main">
				<Menu v-model:is-collapse="isCollapse" />
			</div>
			<span class="theme"
				><ElSwitch
					v-model="theme"
					inline-prompt
					active-text="黑"
					inactive-text="白"
					@click="() => toggleDark()"
			/></span>
		</el-aside>
		<el-container>
			<el-header>
				<TabView />
			</el-header>
			<el-main>
				<!-- mode:  -->
				<!-- in-out：新元素先进行过渡，完成之后当前元素过渡离开。 -->
				<!-- out-in：当前元素先进行过渡，完成之后新元素过渡进入。 -->
				<!-- component key 唯一标识，动画区分不同的内容 -->
				<!-- <router-view v-slot="{ Component, route }">
					<transition mode="out-in" enter-active-class="animate__animated animate__fadeIn">
						<keep-alive>
							<div :key="route.fullPath">
								<component :is="Component" />
							</div>
						</keep-alive>
					</transition>
				</router-view> -->
				<router-view v-slot="{ Component, route }">
					<keep-alive :include="cachedComponents">
						<component :is="Component" :key="route.name" />
					</keep-alive>
				</router-view>
			</el-main>
		</el-container>
	</el-container>
</template>

<script setup lang="ts">
import 'animate.css'
import Menu from './Menu/index.vue'
import { useDarkModeStore, useTabsStore } from '@/store'
import TabView from './Tabs/index.vue'

const { isDark, toggleDark } = useDarkModeStore()

const theme = ref(isDark)

const isCollapse = ref(true)
const route = useRoute()

const tabsStore = useTabsStore()

const cachedComponents = computed(() => tabsStore.getCachedComponents)
const router = useRouter()
const onKeydown = (e: KeyboardEvent) => {
	if (e.key === 'F5') {
		e.preventDefault()

		// 捕获当前路由路径 / tab 信息，避免异步中引用变动的变量
		const currentFullPath = route.fullPath
		const tab = tabsStore.tabs.find((t) => t.id === currentFullPath)

		// 简单防护：确保 router 可用
		if (!router || typeof router.replace !== 'function') {
			console.warn('router not ready, skip refresh')
			return
		}

		const doRedirect = async (targetPath: string) => {
			try {
				// 先导航到 /redirect 前缀，再回到目标路由以触发组件重建
				await router.replace({ path: '/redirect' + targetPath })
				await router.replace(targetPath)
			} catch (err) {
				console.error('redirect refresh failed', err)
			}
		}

		// 如果有 cache 标识，通过删除缓存并走 /redirect 手段重建组件
		if (tab?.cacheName) {
			tabsStore.cachedComponents.delete(tab.cacheName as string)
			// 延迟恢复缓存并触发重载
			setTimeout(() => {
				try {
					tabsStore.cachedComponents.add(tab.cacheName as string)
				} catch (err) {
					console.warn('re-add cache failed', err)
				}
				void doRedirect(currentFullPath)
			}, 120)
		} else {
			void doRedirect(currentFullPath)
		}
	}
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>
<style scoped lang="scss">
@import './index.scss';
.el-header,
.el-main {
	padding-top: 20px;
}
</style>
<style>
.el-menu,
.el-menu-item,
.el-sub-menu,
.el-sub-menu__title {
	background-color: transparent;
	--el-menu-level: 0;
	--el-menu-active-color: var(--el-color-primary) !important;
	--el-menu-text-color: var(--el-text-color-primary) !important;
	--el-menu-hover-text-color: var(--el-color-primary) !important;
	--el-menu-bg-color: var(--el-fill-color-blank) !important;
	--el-menu-hover-bg-color: var(--el-color-primary-light-9) !important;
}
</style>
