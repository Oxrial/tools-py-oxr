<template>
	<el-form :model="data" size="small">
		<FormOperation :btns="btns" />
		<EditTable border :formName="'commands'" :data="data" :columns="columns">
			<template #operation="{ $index }">
				<el-button link type="danger" @click="data.commands.splice($index, 1)">删除</el-button>
			</template>
		</EditTable>
	</el-form>
</template>

<script setup lang="ts">
import EditTable from '@/components/form-module/edit-form-table/index.vue'
import FormOperation from '@/components/form-module/form-operation/index.vue'
import apis from '@/util/api'
import { ElInput } from 'element-plus'
const columns = reactive(
	markRaw([
		{
			label: '标识',
			prop: 'name',
			rules: [{ required: true, message: '必填项', trigger: 'blur' }],
			col: { width: 150 }
		},
		{
			label: 'ffmpeg命令',
			prop: 'command',
			type: ElInput,
			com: { type: 'textarea', spellcheck: false, autosize: { minRows: 1 } },
			rules: [{ required: true, message: '必填项', trigger: 'blur' }]
		},
		{
			label: '备注（占位符）',
			prop: 'description',
			type: ElInput,
			com: { type: 'textarea', spellcheck: false, autosize: { minRows: 1 } },
			col: { width: 200 }
		},
		{
			label: '操作',
			prop: 'operation',
			slot: 'operation',
			col: { width: 100 }
		}
	])
)
const data = reactive<{ commands: any[] }>({
	commands: []
})
const btns = [
	{
		label: '新增',
		type: 'primary',
		icon: 'el-icon-plus',
		onClick: () => data.commands.push({})
	},
	{
		label: '全部保存',
		type: 'primary',
		icon: 'el-icon-finished',
		onClick: () => {
			apis.saveFfmpegCommands(data.commands).then((res) => {
				ElMessage({ message: res.message, type: 'success' })
				loadingFFmpegCommands()
			})
		}
	}
]
const loadingFFmpegCommands = () => {
	apis.getFfmpegCommands().then((res) => {
		if (res?.data?.length) {
			data.commands.splice(0, data.commands.length, ...res.data)
		}
	})
}
onMounted(() => {
	loadingFFmpegCommands()
})
</script>

<style lang="scss" scoped></style>
