import { camelCase } from 'lodash-es'
import req from './request'
import { typesof } from './index'
const apiArr = ['/selectFolder', ['/scanFiles'], ['/creatFilelistForMerge']]
const apis = {}
apiArr.forEach((a) => {
	switch (typesof(a)) {
		case 'string':
			apis[camelCase(a)] = (params) => req[1](a, params)
			break
		case 'array':
			const [url, method] = a
			apis[camelCase(url)] = (params) => req[method || 2](url, params)
	}
})
console.log(apis)
export default apis
