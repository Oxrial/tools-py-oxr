<template>
	<el-form :model="data"> <EditTable border :formName="'table1'" :data="data" :columns="columns" /></el-form>
</template>

<script setup lang="ts">
import EditTable from '@/components/form-module/edit-form-table/index.vue'
const data = reactive({
	table1: [
		{ name: '姓名', label: 'name', age: '150', gender: 0 },
		{ name: '年龄', label: 'age', age: '80', gender: 1 },
		{ name: '地址', label: 'address', age: '200', gender: 0 }
	]
})
const columns = reactive([
	{
		label: '姓名',
		prop: 'name'
	},
	{
		label: '年龄',
		prop: 'age'
	},
	{
		label: '性别',
		prop: 'gender',
		options: [
			{ label: 'W', value: 0 },
			{ label: 'M', value: 1 }
		]
	},
	{
		label: '地址',
		prop: 'label'
	}
])
</script>

<style lang="scss" scoped></style>
