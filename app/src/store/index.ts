import { defineStore } from 'pinia'
import { useDark, useToggle } from '@vueuse/core'

export const useDarkModeStore = defineStore('darkMode', () => {
	const isDark = useDark({
		// 默认值
		initialValue: 'dark',
		storageKey: 'DARK_MODE',
		// 暗黑class名字
		valueDark: 'dark',
		// 高亮class名字
		valueLight: 'light',
		listenToStorageChanges: true,
		initOnMounted: true,
		mergeDefaults: true
	})
	const toggleDark = useToggle(isDark)
	return { isDark, toggleDark }
})
