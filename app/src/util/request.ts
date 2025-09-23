import axios, { type AxiosRequestConfig } from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import type { LoadingInstance } from 'element-plus/es/components/loading/src/loading.mjs'
import { tr } from 'element-plus/es/locales.mjs'
import qs from 'qs'

declare global {
	interface Window {
		loading?: LoadingInstance
	}
}
// create an axios instance
const service = axios.create({
	baseURL: import.meta.env.VITE_APP_BASE_API, // url = base url + request url
	// withCredentials: true, // send cookies when cross-domain requests
	timeout: 5000, // request timeout,
	headers: {
		'Content-Type': 'application/json;charset=utf-8'
	}
})
// request interceptor
service.interceptors.request.use(
	(config) => {
		;(config as any).loading && (window.loading = ElLoading.service({ fullscreen: true }))
		return config
	},
	(error) => {
		console.log(error) // for debug
		return Promise.reject(error)
	}
)
const check = (res: { status: number; message: any }) => {
	if (res.status === 0) {
		ElMessage({ message: res.message || 'No Data', type: 'info', duration: 5 * 1000 })
	} else if (res.status === 1) {
		return true
	} else {
		ElMessage({ message: res.message || 'ERROR', type: 'error', duration: 5 * 1000 })
	}
	return false
}
// response interceptor
service.interceptors.response.use(
	(response) => {
		const res = response.data
		let re = false
		window.loading?.close()
		if (res instanceof Blob) {
			if (response.headers['content-type'] === 'application/json') {
				const reader = new FileReader()
				reader.readAsText(res, 'utf-8')
				reader.onload = function () {
					if (typeof reader.result === 'string') {
						re = check(JSON.parse(reader.result))
					}
				}
			}
			return res
		} else {
			re = check(res)
		}
		return re ? res : Promise.reject(new Error(res.message || 'ERROR'))
	},
	(error) => {
		if (error.response && error.response.status === 401) {
			// singleMsg(error.config.url)
		} else {
			ElMessage({
				message: error.message,
				type: 'error',
				duration: 5 * 1000
			})
		}
		window.loading?.close()
		console.log('err ' + error) // for debug
	}
)

// 统一params传参，与Content-Type无关
export const get = (url: string, params = {}, loading?: boolean, restConfig?: AxiosRequestConfig<any>) =>
	service({ method: 'get', url, params, ...(loading !== undefined ? { loading } : {}), ...restConfig })
// json - post
export const post = (url: string, data = {}, loading?: boolean, restConfig?: AxiosRequestConfig<any>) =>
	service({ method: 'post', url, data, ...(loading !== undefined ? { loading } : {}), ...restConfig })
// formdata - post
const formDataService = (url: string, data = {}, restConfig: AxiosRequestConfig<any>) =>
	service({
		url,
		data: qs.stringify(data),
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		...restConfig
	})
export const fpost = (url: string, data = {}, loading?: boolean, restConfig?: any) =>
	formDataService(url, data, { method: 'post', ...(loading !== undefined ? { loading } : {}), ...restConfig })
// formdata - post - multipart
export const uploadPost = (url: string, formData: any, loading?: boolean, restConfig?: AxiosRequestConfig<any>) =>
	service({
		method: 'post',
		url,
		data: formData,
		...(loading !== undefined ? { loading } : {}),
		headers: {
			'Content-Type': 'multipart/form-data' // 可省略，浏览器自动设置
		},
		...restConfig
	})
const req = {
	1: get,
	2: post,
	21: fpost,
	22: uploadPost
}
export type Req = typeof req
export default req
