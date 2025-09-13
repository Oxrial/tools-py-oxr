<template>
	<div class="operation-bar">
		<ElButton @click="selectFolder" type="primary" plain> 选择文件夹 </ElButton>
		<ElButtonGroup>
			<ElInput
				v-model="folderPath"
				placeholder="键入地址"
				@focus="() => (disabledScan = true)"
				@blur="() => (disabledScan = false)"
			>
			</ElInput>
			<ElInput v-model="fileName" placeholder="文件名" style="width: 30rem"> </ElInput>
			<ElButton :disabled="!showFiles.length" type="success" plain @click="confirmAndMerge"
				>生成 ({{ submit.length }}/{{ showFiles.length }}/{{ sortedFiles.length }})</ElButton
			>
		</ElButtonGroup>
	</div>
	<ElSelect v-model="docmd" placeholder="请选择指令" :options="cmds" />
	<div>
		<ElCard class="flv-list">
			<VueDraggable v-model="sortedFiles" ghostClass="ghost" target="tbody" :animation="150">
				<el-table :data="showFiles" :cell-class-name="renderCellClass" height="calc(100vh - 13rem)">
					<el-table-column prop="name" :width="getColumnWidth('name', sortedFiles)">
						<template #header>
							<el-input v-model="ext" size="small">
								<template #prepend>文件名(.*)</template>
							</el-input>
						</template>
					</el-table-column>
					<el-table-column show-overflow-tooltip label="全路径" prop="id" />
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
	</div>
</template>

<script setup>
import { ref, watch, watchEffect } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { callSuccess, getColumnWidth } from '@/util'
import apis from '@/util/api'
import { join } from 'path-browserify'
import { ElSelect } from 'element-plus'
const folderPath = ref('')
const fileName = ref('')
const files = ref([])
const sortedFiles = ref([])
const disabledScan = ref(false)
const ext = ref()
const selectFolder = async () => {
	await apis.selectFolder({}, true, { timeout: 300000 }).then((res) => {
		folderPath.value = res.data.folder_path
	})
}
const cmds = ref([])
const getCmds = () => {
	apis.getFfmpegCommands().then((res) => {
		cmds.value = res.data.map((c) => ({ label: c.name, value: c.command }))
	})
}
onMounted(getCmds)
const docmd = ref()
const showFiles = ref([])
const scanFlvFiles = async (folder) => {
	if (disabledScan.value || !folder.length) return
	await apis.scanFiles({ path: folder }).then((res) => {
		files.value = res.data.files || []
		sortedFiles.value.splice(
			0,
			sortedFiles.value.length,
			...files.value.map((f) => ({
				name: f.substring(f.lastIndexOf('/') + 1),
				id: f,
				delete: false
			}))
		)
	})
}

watch(showFiles, () => {
	if (showFiles.value.length) {
		fileName.value = 'output_' + showFiles.value[0].name
	}
})
const renderCellClass = (data) => {
	return data.row.delete && data.columnIndex !== 2 ? ' delete' : ''
}
watchEffect(() => {
	scanFlvFiles(folderPath.value)
})
watchEffect(
	() =>
		(showFiles.value = sortedFiles.value.filter(
			(f) => f.name.match(new RegExp(ext.value, 'i')) || f.name.includes(ext.value)
		))
)
const submit = computed(() =>
	sortedFiles.value
		.filter((s) => !s.delete && (s.name.match(new RegExp(ext.value, 'i')) || s.name.includes(ext.value)))
		.map((s) => s.id)
)
const confirmAndMerge = async () => {
	await apis
		.createFilelistMerge({
			files: submit.value,
			folderPath: folderPath.value,
			fileName: fileName.value
		})
		.then(callSuccess)
}
</script>
<style scoped lang="scss">
.operation-bar {
	width: 100%;
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
</style>
<style lang="scss">
.ghost {
	background: rgb(219, 219, 219) !important;
}
</style>
