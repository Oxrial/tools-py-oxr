<template>
	<el-container>
		<el-aside width="auto">
			<div class="aside-main">
				<Menu v-model:is-collapse="isCollapse" />
			</div>
		</el-aside>
		<el-container>
			<el-header>
				<div class="nav-bar">
					<span>Tools-OXR</span>
					<span class="theme">白<ElSwitch v-model="theme" @click="() => toggleDark()" />黑</span>
				</div>
			</el-header>
			<el-main>
				<router-view v-slot="{ Component, route }">
					<!-- mode:  -->
					<!-- in-out：新元素先进行过渡，完成之后当前元素过渡离开。 -->
					<!-- out-in：当前元素先进行过渡，完成之后新元素过渡进入。 -->
					<!-- component key 唯一标识，动画区分不同的内容 -->
					<transition mode="out-in" enter-active-class="animate__animated animate__fadeIn">
						<keep-alive>
							<div :key="route.fullPath">
								<component :is="Component" />
							</div>
						</keep-alive>
					</transition>
				</router-view>
			</el-main>
		</el-container>
	</el-container>
</template>

<script setup lang="ts">
import 'animate.css'
import Menu from './Menu/index.vue'
import { useDarkModeStore } from '@/store'

const { isDark, toggleDark } = useDarkModeStore()

const theme = ref(isDark)

const isCollapse = ref(true)
</script>
<style scoped lang="scss">
@import './index.scss';
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
