import { camelCase } from 'lodash-es'
import req, { type Req } from './request'
import { typesof } from '@/util'

const apiArr: Array<string | [string, number?]> = ['/select-folder', '/scan-files', ['/create-filelist-merge']]
const API_NAMES = apiArr
	.flat()
	.filter((f) => typesof(f) === 'string')
	.map((f) => camelCase(f as string)) // 去掉前导斜杠

type ApiName = (typeof API_NAMES)[number]

type ApiFunctions = {
	[K in ApiName]: (params: object) => Promise<any>
}

const apisObj: Record<string, (params: object) => Promise<any>> = {}

apiArr.forEach((a) => {
	switch (typeof a) {
		case 'string':
			apisObj[camelCase(a)] = (params, loading = false, headers = {}) => req[1](a, params, loading, headers)
			break
		case 'object':
			const [url, method] = a
			apisObj[camelCase(url)] = (params, loading = false, headers = {}) =>
				req[(method as keyof Req) || 2](url, params, loading, headers)
	}
})

export default apisObj as ApiFunctions
