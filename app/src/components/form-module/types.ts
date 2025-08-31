import type { FormItemRule } from 'element-plus'
export interface FormItemDefaultProps {
	label: string
	prop: string
	type?: string
	subType?: string
	options?: { [key: string]: any }[]
	width?: string
	minWidth?: string
	col?: object
	ite?: object
	com?: object
	rules?: FormItemRule[]
}
export type FormItemProps = Omit<FormItemDefaultProps, 'col'>
