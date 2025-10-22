<template>
	<DbTable
		header="FFmpeg 指令"
		:data="data"
		form-name="commands"
		:columns="ffmpegColumns"
		get-api="getFfmpegCommands"
		save-api="saveFfmpegCommands"
		@update:data="(d) => data['commands'].splice(0, data['commands'].length, ...d)"
		@push:data="() => data['commands'].push({})"
	/>
	<DbTable
		header="配置参数"
		:data="data"
		form-name="confs"
		:columns="paramsColumns"
		get-api="getConfParam"
		save-api="saveConfParam"
		@update:data="(d) => data['confs'].splice(0, data['confs'].length, ...d)"
		@push:data="() => data['confs'].push({})"
	/>
</template>

<script setup lang="ts">
import DbTable from './module/db-table.vue'
import { ElInput } from 'element-plus'
interface FFmpeg {
	name: string
	command: string
	description: string
}
interface Param {
	pkey: string
	pvalue: string
}
const data = reactive<{ commands: Array<FFmpeg | any>; confs: Array<Param | any> }>({ commands: [], confs: [] })
const ffmpegColumns = shallowReactive([
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
const paramsColumns = shallowReactive([
	{
		label: '键',
		prop: 'pkey',
		rules: [{ required: true, message: '必填项', trigger: 'blur' }],
		col: { width: 150 }
	},
	{
		label: '值',
		prop: 'pvalue'
	}
])
</script>

<style lang="scss" scoped></style>
