<template>
	<el-form :model="data">
		<EditTable border :formName="'table1'" :data="data" :columns="columns" />
		<FormOperation
			:btns="[
				{ label: '新增', type: 'primary', icon: 'el-icon-plus', slot: 'add' },
				{ label: '删除', type: 'danger', icon: 'el-icon-delete', slot: 'delete' }
			]"
		/>
	</el-form>
</template>

<script setup lang="ts">
import EditTable from '@/components/form-module/edit-form-table/index.vue'
import FormOperation from '@/components/form-module/form-operation/index.vue'
const data = reactive({
	table1: [{ id: '1', name: '姓名', command: 'name', description: '150' }]
})
const columns = reactive([
	{
		label: '标识',
		prop: 'name',
		rules: [{ required: true, message: '必填项', trigger: 'blur' }]
	},
	{
		label: 'ffmpeg命令',
		prop: 'command',
		rules: [{ required: true, message: '必填项', trigger: 'blur' }]
	},
	{
		label: '备注',
		prop: 'description',
		rules: [{ required: true, message: '必填项', trigger: 'blur' }]
	}
])
</script>

<style lang="scss" scoped></style>
