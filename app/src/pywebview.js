let api = {}

// 检测是否在PyWebView环境中
if (window.pywebview) {
	api = window.pywebview.api
} else {
	// 开发环境模拟API
	api = {
		get_system_info: () =>
			Promise.resolve({
				os: 'Development',
				version: '1.0.0',
				cpu_usage: 15,
				memory_usage: 30
			}),
		save_file: (content) =>
			Promise.resolve({
				status: 'success',
				path: '~/Documents/mock_file.txt'
			}),
		show_notification: (title, message) =>
			Promise.resolve({
				status: 'shown'
			})
	}
}

// 封装API方法
export const getSystemInfo = async () => {
	try {
		return await api.get_system_info()
	} catch (error) {
		console.error('获取系统信息失败:', error)
		return null
	}
}

export const saveFile = async (content) => {
	try {
		return await api.save_file(content)
	} catch (error) {
		console.error('保存文件失败:', error)
		return { status: 'error', message: error.message }
	}
}

export const showNotification = async (title, message) => {
	try {
		return await api.show_notification(title, message)
	} catch (error) {
		console.error('显示通知失败:', error)
		return { status: 'error' }
	}
}

export default {
	getSystemInfo,
	saveFile,
	showNotification
}
