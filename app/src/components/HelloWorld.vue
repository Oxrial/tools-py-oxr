<template>
	<div class="home-container">
		<!-- 标题栏 -->
		<div class="title-bar">
			<div class="drag-area"></div>
			<div class="window-controls">
				<button @click="minimize">—</button>
				<button @click="maximize">□</button>
				<button @click="close">×</button>
			</div>
		</div>

		<!-- 内容区 -->
		<div class="content">
			<h1>PyWebView + Vue3 桌面应用</h1>

			<div class="system-info">
				<h2>系统信息</h2>
				<button @click="fetchSystemInfo">获取系统信息</button>
				<div v-if="systemInfo">
					<p>操作系统: {{ systemInfo.os }}</p>
					<p>版本: {{ systemInfo.version }}</p>
					<p>CPU使用率: {{ systemInfo.cpu_usage }}%</p>
					<p>内存使用率: {{ systemInfo.memory_usage }}%</p>
				</div>
			</div>

			<div class="file-operations">
				<h2>文件操作</h2>
				<textarea v-model="fileContent" placeholder="输入文件内容..."></textarea>
				<button @click="saveFile">保存文件</button>
				<p v-if="saveResult">{{ saveResult }}</p>
			</div>

			<div class="notification">
				<h2>通知测试</h2>
				<button @click="showTestNotification">发送通知</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { getSystemInfo, saveFile, showNotification } from '../pywebview'

const systemInfo = ref(null)
const fileContent = ref('')
const saveResult = ref('')

const fetchSystemInfo = async () => {
	systemInfo.value = await getSystemInfo()
}

const saveFileContent = async () => {
	if (!fileContent.value.trim()) {
		saveResult.value = '内容不能为空'
		return
	}

	const result = await saveFile(fileContent.value)
	if (result.status === 'success') {
		saveResult.value = `文件保存成功: ${result.path}`
		fileContent.value = ''
	} else {
		saveResult.value = '文件保存失败'
	}
}

const showTestNotification = () => {
	showNotification('应用通知', '这是一条来自PyWebView+Vue3应用的通知')
}

// 窗口控制
const minimize = () => {
	if (window.pywebview) {
		window.pywebview.window.minimize()
	}
}

const maximize = () => {
	if (window.pywebview) {
		window.pywebview.window.toggle_fullscreen()
	}
}

const close = () => {
	if (window.pywebview) {
		window.pywebview.window.destroy()
	}
}
</script>

<style scoped>
.home-container {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: #f5f7fa;
}

.title-bar {
	height: 32px;
	background: #2c3e50;
	display: flex;
	justify-content: space-between;
	align-items: center;
	-webkit-app-region: drag;
}

.drag-area {
	flex: 1;
	height: 100%;
}

.window-controls {
	display: flex;
	height: 100%;
	-webkit-app-region: no-drag;
}

.window-controls button {
	width: 40px;
	height: 100%;
	border: none;
	background: transparent;
	color: white;
	font-size: 16px;
	cursor: pointer;
}

.window-controls button:hover {
	background: rgba(255, 255, 255, 0.2);
}

.content {
	flex: 1;
	padding: 20px;
	overflow-y: auto;
}

.system-info,
.file-operations,
.notification {
	margin-bottom: 30px;
	padding: 20px;
	background: white;
	border-radius: 8px;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

textarea {
	width: 100%;
	height: 100px;
	padding: 10px;
	margin: 10px 0;
	border: 1px solid #dcdfe6;
	border-radius: 4px;
	resize: vertical;
}

button {
	padding: 8px 16px;
	background: #3498db;
	color: white;
	border: none;
	border-radius: 4px;
	cursor: pointer;
	transition: background 0.3s;
}

button:hover {
	background: #2980b9;
}
</style>
