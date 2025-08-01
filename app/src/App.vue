<template>
	<div class="main">
		<div class="nav-bar">
			<span>Tools-OXR</span>
			<span class="theme">白<ElSwitch v-model="theme" @click="() => toggleDark()" />黑</span>
		</div>
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
				<ElButton :disabled="!sortedFiles.length" type="success" plain @click="confirmAndMerge"
					>生成 ({{ submit.length }}/{{ sortedFiles.length }})</ElButton
				>
			</ElButtonGroup>
		</div>
		<div>
			<ElCard class="flv-list" v-if="sortedFiles.length">
				<VueDraggable v-model="sortedFiles" ghostClass="ghost" target="tbody" :animation="150">
					<el-table :data="sortedFiles" :cell-class-name="renderCellClass" height="calc(100vh - 12rem)">
						<el-table-column label="文件名" prop="name" :width="getColumnWidth('name', sortedFiles)" />
						<el-table-column show-overflow-tooltip="" label="全路径" prop="id" />
						<el-table-column label="操作" width="70">
							<template #default="scope">
								<el-button link type="primary" size="small" @click="handleDelete(scope.row)">
									{{ scope.row.delete ? '撤销' : '屏蔽' }}
								</el-button>
							</template>
						</el-table-column>
					</el-table>
				</VueDraggable>
			</ElCard>
		</div>
	</div>
</template>

<script setup>
import { ref, watch, watchEffect } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { getColumnWidth } from '@/util'
import apis from '@/util/api'
console.log('🚀 ~ file: App.vue ~ line 1 ~ apis:', apis)
import { join } from 'path-browserify'
import { useDark, useToggle } from '@vueuse/core'

const theme = ref(false)
const isDark = useDark()
const toggleDark = useToggle(isDark)

const folderPath = ref('')
const fileName = ref('')
const files = ref([])
const sortedFiles = ref([])
const disabledScan = ref(false)
const selectFolder = async () => {
	folderPath.value = await apis.selectFolder().then((res) => {})
	// scanFlvFiles(folderPath.value)
}
const scanFlvFiles = async (folder) => {
	if (disabledScan.value || !folder.length) return
	files.value = await apis.scanFiles({ path: folder })
	sortedFiles.value.splice(
		0,
		sortedFiles.value.length,
		...files.value.map((f) => ({
			name: f.substring(f.lastIndexOf('/') + 1),
			id: join(folder, f),
			delete: false
		}))
	)
	if (sortedFiles.value.length) {
		const n = sortedFiles.value[0].name
		fileName.value =
			folder.substring(folder.lastIndexOf('\\') + 1) + n.substring(n.lastIndexOf('-'), n.indexOf('.'))
	}
	console.log('🚀 ~ selectFolder ~ files:', sortedFiles)
}

const handleDelete = (row) => {
	row.delete = !row.delete
}
const renderCellClass = (data) => {
	return (data.columnIndex === 0 ? 'flv-name ' : '') + (data.row.delete && data.columnIndex !== 2 ? ' delete' : '')
}
watchEffect(() => {
	scanFlvFiles(folderPath.value)
})
const submit = computed(() => sortedFiles.value.filter((s) => !s.delete).map((s) => s.id))
const confirmAndMerge = async () => {
	try {
		await apis.creatFilelistForMerge({
			files: submit.value,
			folderPath: folderPath.value,
			fileName: fileName.value
		})
		ElMessage({ message: '视频合并完成！', type: 'success' })
	} catch (error) {
		ElMessage({ message: `Error: ${error}`, type: 'error' })
	}
}
</script>
<style scoped lang="scss">
.main {
	padding: 20px 20px 0;
	.nav-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding-bottom: 20px;
		.title {
			font-size: 2rem;
			font-weight: bold;
		}
		.theme {
			display: flex;
			align-items: center;
		}
	}
}
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
:deep(.flv-name) {
	width: fit-content;
}
</style>
<style lang="scss">
.ghost {
	background: rgb(219, 219, 219) !important;
}
</style>
