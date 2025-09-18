<template>
	<div class="operation-bar">
		<ElButton @click="selectFiles" type="primary" plain> 选择文件 </ElButton>
		<ElButtonGroup>
			<ElSelect v-model="docmd" placeholder="请选择指令">
				<ElOption
					v-for="item in cmds"
					:key="item.value"
					:label="`${item.label} - [ ${item.value} ]`"
					:value="item.value"
				/>
			</ElSelect>
			<ElInput v-model="fileExt" placeholder="转换后文件类型" style="width: 10%" />
			<ElButton :disabled="!showFiles.length || !docmd" type="success" plain @click="confirmAndMerge"
				>生成 ({{ submit.length }}/{{ showFiles.length }}/{{ sortedFiles.length }})</ElButton
			>
		</ElButtonGroup>
	</div>
	<ElCard class="flv-list">
		<VueDraggable v-model="sortedFiles" ghostClass="ghost" target="tbody" :animation="150">
			<el-table :data="showFiles" :cell-class-name="renderCellClass" height="calc(100vh - 16rem)">
				<el-table-column prop="name" :width="getColumnWidth('name', sortedFiles)">
					<template #header>
						<el-input v-model="ext" size="small">
							<template #prepend>文件名(.*)</template>
						</el-input>
					</template>
				</el-table-column>
				<el-table-column show-overflow-tooltip label="全路径" prop="id" />
				<el-table-column show-overflow-tooltip label="输出预览" prop="conv" />
				<el-table-column label="操作" width="70">
					<template #default="{ row }">
						<el-button link type="primary" size="small" @click="() => (row.delete = !row.delete)">
							{{ row.delete ? '撤销' : '屏蔽' }}
						</el-button>
					</template>
				</el-table-column>
			</el-table>
		</VueDraggable>
	</ElCard>
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { callSuccess, getColumnWidth } from '@/util'
import apis from '@/util/api'
import { ElSelect } from 'element-plus'
const fileExt = ref('m4a')
const files = ref([])
const sortedFiles = ref([])
const ext = ref()
const selectFiles = async () => {
	await apis.selectFiles({}, true, { timeout: 300000 }).then((res) => {
		files.value = res.data.file_paths
		sortedFiles.value.splice(
			0,
			sortedFiles.value.length,
			...files.value.map((f) => ({
				name: f.substring(f.lastIndexOf('/') + 1),
				id: f,
				delete: false,
				conv: fileExt.value
					? f.substring(f.lastIndexOf('/') + 1, f.lastIndexOf('.') + 1) + fileExt.value
					: f.substring(f.lastIndexOf('/') + 1)
			}))
		)
	})
}
const cmds = ref([])
const getCmds = () => {
	apis.getFfmpegCommands().then((res) => {
		cmds.value = res.data
			.filter((c) => c.name.includes('CONV_'))
			.map((c) => ({ label: c.name, value: c.command }))
			.sort((a, b) => a.label.localeCompare(b.label))
	})
}
onMounted(getCmds)
const docmd = ref()
const showFiles = ref([])

const renderCellClass = (data) => {
	return data.row.delete && data.columnIndex !== 2 ? ' delete' : ''
}
watchEffect(
	() =>
		(showFiles.value = sortedFiles.value.filter(
			(f) => f.name.match(new RegExp(ext.value, 'i')) || f.name.includes(ext.value)
		))
)
const submit = computed(() =>
	sortedFiles.value
		.filter((s) => !s.delete && (s.name.match(new RegExp(ext.value, 'i')) || s.name.includes(ext.value)))
		.map((s) => ({ id: s.id, conv: s.id.substring(0, s.id.lastIndexOf('.') + 1) + fileExt.value }))
)
const confirmAndMerge = async () => {
	await apis
		.createFilelistMerge({
			convFiles: submit.value,
			cmd: docmd.value
		})
		.then(callSuccess)
}
</script>
<style scoped lang="scss">
.operation-bar {
	display: flex;
	padding-bottom: 20px;
	> :last-child {
		flex: 1;
		display: flex;
		> :last-child {
			width: 30%;
			&.is-disabled {
				background-color: #0001;
			}
		}
	}
}
:deep(.el-input-group__prepend) .el-button {
	all: unset;
}
:deep(.delete) {
	filter: brightness(0.96) blur(1px);
}
.flv-list {
	margin-top: 20px;
}
</style>
<style lang="scss">
.ghost {
	background: rgb(219, 219, 219) !important;
}
</style>
