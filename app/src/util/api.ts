import { camelCase } from 'lodash-es'
import req, { type Req } from '@/util/request'
import apiArr from '@/api'
/*
	从形如 '/path/name_method' 的字符串中提取路径部分，去掉方法后缀
	使用TypeScript条件类型，如果字符串匹配 `${infer U}_${number}` 模式，则提取U部分，否则返回原字符串
*/
type ExtractUrlPart<T> = T extends `${infer U}_${number}` ? U : T

/*
	将路径字符串转换为驼峰命名
	处理路径分隔符 '/'，递归处理前后两部分
	处理连字符 '-'，将后半部分首字母大写实现驼峰命名
	如果没有特殊字符，直接返回原字符串
*/

// prettier-ignore
type CamelCase<S extends string> = S extends `${infer P1}/${infer P2}`
	? // 如果包含路径分隔符，递归处理并组合
		`${CamelCase<P1>}${Capitalize<CamelCase<P2>>}`
	: S extends `${infer P1}-${infer P2}`
		? `${CamelCase<P1>}${Capitalize<CamelCase<P2>>}`
		: S

/* 
	T 必须是 string 类型或其子类型
	由于 string 是基本类型，实际上 T 可以是：
	基本 string 类型
	字符串字面量类型（如 "hello"）
	字符串字面量联合类型（如 "a" | "b"）
	模板字面量类型（如 `id-${number}`）
 */
type ApiToFunction<T extends string> = {
	/* 
		K in T 表示遍历传入的字符串字面量类型联合
		as CamelCase<ExtractUrlPart<K>> 表示使用映射类型将原始键名转换为驼峰命名的函数名 
	*/
	[K in T as Uncapitalize<CamelCase<ExtractUrlPart<K>>>]: (
		params?: any,
		loading?: boolean,
		headers?: any
	) => Promise<any>
}

// 从apiArr中提取所有元素的联合类型，即 '/select-folder' | '/scan-files' | ...
type ApiKeys = (typeof apiArr)[number]

// 使用类型断言创建api对象，指定其类型为ApiToFunction<ApiKeys>，这样可以获得完整的类型提示
const apiObj = {} as ApiToFunction<ApiKeys>

// 遍历API数组，为每个API项创建对应的函数
apiArr.forEach((item) => {
	// 将item按_分割为url和method两部分，如果没有指定method则默认为'1'(get请求)
	// 使用类型断言指定url为string类型，method为Req的key或者undefined
	const [url, method = '1'] = item.split('_') as [string, keyof Req | undefined]

	// 使用lodash的camelCase函数将url转换为驼峰命名，并断言为apiObj的key类型
	const key = camelCase(url) as keyof typeof apiObj

	// 为apiObj添加对应的方法
	// 使用传入的method或默认的'1'(get方法)调用req发起请求
	// 添加到 apiObj 并保留类型安全
	apiObj[key] = ((params: any = {}, loading = false, headers = {}) =>
		req[method](url, params, loading, headers)) as any
})

// 导出具有完整类型提示的api对象
export default apiObj
