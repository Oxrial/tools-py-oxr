/*
    定义API数组，使用 as const 转换为只读元组字面量类型，这样可以保留每个元素的具体类型信息
    其中URL后可选添加 _数字 表示请求方法，1=get, 2=post, 21=formdata-post, 22=文件上传
 */
const apiArr = [
	'/select-folder',
	'/scan-files',
	'/create-filelist-merge_2',
	'/save-ffmpeg-commands_2',
	'/get-ffmpeg-commands',
	'/select-files',
	'/convert-media_2',
	'/save-conf-param_2',
	'/get-conf-param'
] as const
export default apiArr
