<template>
	<el-table class="edit-form-table" :data="data[formName]" v-bind="omit(props, 'data', 'formName', 'columns')">
		<el-table-column
			v-for="f in columns"
			:key="f.prop"
			:label="f.label"
			:prop="f.prop"
			:width="f.width"
			:min-width="f.minWidth"
			v-bind="f.col"
		>
			<template #default="{ row, column, $index }">
				<el-form-item :prop="`data.${formName}.${$index}.${f.prop}`" :rules="f.rules" v-bind="f.ite">
					<component v-if="!f.options?.length" v-bind="f.com" v-model="row[f.prop]" :is="f.type || ElInput" />
					<component
						v-else-if="f.options.length"
						v-bind="f.com"
						v-model="row[f.prop]"
						:is="f.type || ElSelect"
					>
						<component
							v-for="op in f.options"
							:is="f.subType || ElOption"
							:label="op.label"
							:value="op.value"
							v-bind="omit(op, 'label', 'value')"
						></component>
					</component>
				</el-form-item>
			</template>
		</el-table-column>
	</el-table>
</template>

<script setup lang="ts">
import type { FormItemRule } from 'element-plus'
import { omit } from 'lodash-es'
import { ElInput, ElSelect, ElOption } from 'element-plus'
import { fchmodSync } from 'fs-extra'

interface FormItemProps {
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
const props = withDefaults(
	defineProps<{
		[key: string]: any
		formName: string
		data: { [key: string]: any }
		columns?: FormItemProps[]
	}>(),
	{ data: () => [], forms: () => [] }
)
</script>

<style lang="scss" scoped>
.edit-form-table {
	width: 100%;
	.el-form-item {
		margin: unset;
	}
}
</style>
