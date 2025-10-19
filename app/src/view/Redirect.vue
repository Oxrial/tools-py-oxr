<!-- views/Redirect.vue -->
<template>
	<div></div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

onMounted(() => {
	const { params, query } = route
	const { path } = params

	// 移除 /redirect 前缀，恢复原始路径
	const originalPath = Array.isArray(path) ? path.join('/') : path

	router.replace({
		path: originalPath.startsWith('/') ? originalPath : '/' + originalPath,
		query
	})
})
</script>
