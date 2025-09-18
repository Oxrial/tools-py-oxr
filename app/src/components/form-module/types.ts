import type { FormItemRule } from 'element-plus'
import type { Component } from 'vue'
export interface FormItemDefaultProps {
	label: string
	prop: string
	slot?: string
	type?: string | Component
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
