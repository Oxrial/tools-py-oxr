/**
 * 表格列宽自适应
 * @param prop 属性
 * @param records 数据
 * @param minWidth 最小宽度
 */
const getColumnWidth = (prop, records, minWidth = 80) => {
	const padding = 12 // 列内边距

	const contentWidths = records.map((item) => {
		const value = item[prop] ? String(item[prop]) : ''
		const textWidth = getTextWidth(value)
		return textWidth + padding
	})

	const maxWidth = Math.max(...contentWidths)
	return Math.max(minWidth, maxWidth)
}
/**
 * el-table扩展工具  -- 列宽度自适应 - 获取列宽内文本宽度
 * @param {*} text 文本内容
 * @returns 文本宽度(int)
 */
const getTextWidth = (text) => {
	const span = document.createElement('span')
	span.style.visibility = 'hidden'
	span.style.position = 'absolute'
	span.style.top = '-9999px'
	span.style.whiteSpace = 'nowrap'
	span.style.fontSize = '16px'
	span.innerText = text
	document.body.appendChild(span)
	const width = span.offsetWidth + 16
	document.body.removeChild(span)
	return width
}
export { getColumnWidth }
