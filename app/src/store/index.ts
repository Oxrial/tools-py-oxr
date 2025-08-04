import { defineStore } from 'pinia'
import { useDark, useToggle } from '@vueuse/core'

export const useDarkModeStore = defineStore('darkMode', () => {
	const isDark = useDark({
		// 存储到localStorage/sessionStorage中的Key 根据自己的需求更改
		storageKey: 'DARK_MODE',
		// 暗黑class名字
		valueDark: 'dark',
		// 高亮class名字
		valueLight: 'light'
	})
	const toggleDark = useToggle(isDark)
	return { isDark, toggleDark }
})
