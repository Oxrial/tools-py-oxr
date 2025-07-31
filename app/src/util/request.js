import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import qs from 'qs'
// create an axios instance
const service = axios.create({
	baseURL: import.meta.env.VUE_APP_BASE_API, // url = base url + request url
	// withCredentials: true, // send cookies when cross-domain requests
	timeout: 5000, // request timeout,
	headers: {
		'Content-Type': 'application/json;charset=utf-8'
	}
})
// request interceptor
service.interceptors.request.use(
	(config) => {
		// do something before request is sent
		config.loading && ElLoading.service({ fullscreen: true })
		// if (!whiteList.includes(config.url)) {
		// 	if (getToken()) {
		// 		config.headers['Authorization'] = `Bearer ${getToken()}`
		// 	}
		// }
		return config
	},
	(error) => {
		console.log(error) // for debug
		return Promise.reject(error)
	}
)
const check = (res) => {
	if (res.state === '0') {
		ElMessage({ message: res.message || 'No Data', type: 'info', duration: 5 * 1000 })
	} else if (res.strState !== '1') {
		ElMessage({ message: res.message || 'ERROR', type: 'error', duration: 5 * 1000 })
	}
}
// response interceptor
service.interceptors.response.use(
	(response) => {
		const res = response.data
		response.config.loading && ElLoading.service({ fullscreen: false })
		if (res instanceof Blob) {
			if (response.headers['content-type'] === 'application/json') {
				const reader = new FileReader()
				reader.readAsText(res, 'utf-8')
				reader.onload = function () {
					check(JSON.parse(reader.result))
				}
			}
		} else {
			check(res)
		}
		return res
	},
	(error) => {
		if (error.response && error.response.status === 401) {
			singleMsg(error.config.url)
		} else {
			Message({
				message: error.message,
				type: 'error',
				duration: 5 * 1000
			})
		}
		error.loading && ElLoading.service({ fullscreen: false })
		console.log('err' + error) // for debug
		return Promise.reject(error)
	}
)

// 统一params传参，与Content-Type无关
export const get = (url, params = {}, loading, restConfig) =>
	service({ method: 'get', url, params, loading, ...restConfig })
// json - post
export const post = (url, data = {}, loading, restConfig) =>
	service({ method: 'post', url, data, loading, ...restConfig })
// formdata - post
const formDataService = (url, data = {}, restConfig) =>
	service({
		url,
		data: qs.stringify(data),
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		...restConfig
	})
export const fpost = (url, data = {}, loading, restConfig) =>
	formDataService(url, data, { method: 'post', loading, ...restConfig })
// formdata - post - multipart
export const uploadPost = (url, formData, loading, restConfig) =>
	service({
		method: 'post',
		url,
		data: formData,
		loading,
		headers: {
			'Content-Type': 'multipart/form-data' // 可省略，浏览器自动设置
		},
		...restConfig
	})
export default {
	1: get,
	2: post,
	21: fpost,
	22: uploadPost
}
