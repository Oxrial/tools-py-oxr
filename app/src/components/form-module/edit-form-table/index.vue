<template>
	<el-table class="edit-form-table" :data="data[formName]" v-bind="omit(props, 'data', 'formName', 'columns')">
		<el-table-column
			v-for="f in columns"
			:key="f.prop"
			:label="f.label"
			:prop="f.prop"
			:width="f.width"
			:min-width="f.minWidth"
			class-name="edit-form-column"
			v-bind="f.col"
		>
			<template #default="{ row, $index }">
				<EditFormItem table :prop="`data.${formName}.${$index}.${f.prop}`" :form-item="f" :data="row" />
			</template>
		</el-table-column>
	</el-table>
</template>

<script setup lang="ts">
import type { FormItemDefaultProps } from '../types'
import { omit } from 'lodash-es'
import EditFormItem from '../edit-form-item/index.vue'

const props = withDefaults(
	defineProps<{
		formName: string
		data: { [key: string]: any }
		columns?: FormItemDefaultProps[]
	}>(),
	{ data: () => [], forms: () => [] }
)
</script>

<style lang="scss" scoped>
.edit-form-table {
	width: 100%;
	.edit-form-column {
		position: relative;
	}
	.el-form-item {
		margin: unset;
	}
}
</style>
