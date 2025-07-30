import { defineStore } from 'pinia'

export const useLoadingStore = defineStore('loading', () => {
	const loadingRef = ref(false)
	const setLoading = (flag) => {
		loadingRef.value = flag
	}
	return [loadingRef, setLoading]
})
