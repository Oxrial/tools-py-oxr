<template>
	<el-form :model="data" size="small" style="margin-bottom: 20px">
		<el-card shadow="always">
			<template #header>
				<div class="box-header">
					<div>{{ header }}</div>
					<FormOperation :btns="btns" />
				</div>
			</template>
			<EditTable border :formName="formName" :data="data" :columns="columns">
				<template #operation="{ $index }">
					<el-button link type="danger" @click="data[formName].splice($index, 1)">删除</el-button>
				</template>
			</EditTable>
		</el-card>
	</el-form>
</template>

<script setup lang="ts">
defineOptions({ name: 'ConfigIndex' })
import EditTable from '@/components/form-module/edit-form-table/index.vue'
import FormOperation from '@/components/form-module/form-operation/index.vue'
import apis from '@/util/api'
import type { ApiKey } from '@/util/api'

const props = withDefaults(
	defineProps<{
		header: string
		data: { [key: string]: any }
		formName: string
		columns: any[]
		getApi: string
		saveApi: string
	}>(),
	{}
)

const emits = defineEmits(['update:data', 'push:data'])
const btns = [
	{
		label: '新增',
		type: 'primary',
		icon: 'el-icon-plus',
		onClick: () => emits('push:data')
	},
	{
		label: '全部保存',
		type: 'primary',
		icon: 'el-icon-finished',
		onClick: () => {
			apis[props.saveApi as ApiKey](props.data[props.formName]).then((res) => {
				ElMessage({ message: res.message, type: 'success' })
				loadingTableData()
			})
		}
	}
]
const loadingTableData = () => {
	apis[props.getApi as ApiKey]().then((res) => {
		if (res?.data?.length) {
			emits('update:data', res.data)
		}
	})
}
onMounted(() => {
	loadingTableData()
})
</script>

<style lang="scss" scoped>
.box-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	.el-form-item {
		margin-bottom: 0;
	}
}
</style>
