import axios from 'axios'
import { MessageBox, Message } from 'element-ui'
import qs from 'qs'
// create an axios instance
const service = axios.create({
	baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
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
		config.loading && store.dispatch('setLoading', true)
		if (!whiteList.includes(config.url)) {
			if (getToken()) {
				config.headers['Authorization'] = `Bearer ${getToken()}`
			}
		}
		// if (store.getters.token) {

		//   // let each request carry token
		//   // ['X-Token'] is a custom headers key
		//   // please modify it according to the actual situation
		//   config.headers['X-Token'] = getToken();
		// }
		// if(config.data.indexOf('reqJson')>-1){
		//   config.baseURL = "";
		// }
		return config
	},
	(error) => {
		// do something with request error
		console.log(error) // for debug
		return Promise.reject(error)
	}
)
