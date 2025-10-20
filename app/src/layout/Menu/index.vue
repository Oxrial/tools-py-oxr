<template>
	<div class="logo-main" @click="clickCollapse">
		<transition name="logoTransition" :appear="true" :css="false">
			<span v-if="!isCollapse" class="project-logo">
				<el-image :src="logo" fit="contain" style="height: inherit" /><b>&emsp; Tools-OXR</b></span
			>
			<el-image v-else :src="logo" fit="contain" class="project-logo" />
		</transition>
	</div>
	<el-scrollbar class="submenu-main">
		<el-menu
			router
			:collapse="isCollapse"
			:default-active="defaultActive"
			:background-color="scss.aside_theme"
			text-color="#fefefea6"
			class="el-menu-vertical-demo"
		>
			<sub-menu :menu-data="(routes as any[])" />
		</el-menu>
	</el-scrollbar>
</template>

<script setup lang="ts">
import logo from '@/assets/oxr-192x192.png'
import SubMenu from './Submenu/index.vue'
import { useRouter, useRoute } from 'vue-router'
// import { routesObj } from '@/router'
import scss from '@/assets/style.module.scss'

const props = defineProps({
	isCollapse: {
		type: Boolean,
		default: false
	}
})
const emits = defineEmits(['update:isCollapse'])
const clickCollapse = () => {
	emits('update:isCollapse', !props.isCollapse)
}
const $routes = useRouter()
const $route = useRoute()
const routes = computed(() => $routes.options.routes)

const defaultActive = computed(() => $route.path)
</script>
<style scoped lang="scss">
@import './index.scss';
</style>
