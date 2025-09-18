<template>
	<el-form-item
		:class="table ? 'table-item' : ''"
		:prop="table ? prop : formItem.prop"
		:rules="formItem.rules"
		:key="table ? prop : formItem.prop"
		v-bind="{ ...(table ? { label: ' ' } : pick(formItem, 'label')), ...formItem.ite }"
	>
		<component
			v-if="!formItem.options?.length"
			v-bind="formItem.com"
			v-model="data[formItem.prop]"
			:is="formItem.type || ElInput"
		/>
		<component
			v-else-if="formItem.options.length"
			v-bind="formItem.com"
			v-model="data[formItem.prop]"
			:is="formItem.type || ElSelect"
		>
			<component
				v-for="op in formItem.options"
				:is="formItem.subType || ElOption"
				:label="op.label"
				:value="op.value"
				v-bind="omit(op, 'label', 'value')"
			></component>
		</component>
	</el-form-item>
</template>

<script setup lang="ts">
import type { FormItemProps } from '../types'
import { ElInput, ElSelect, ElOption } from 'element-plus'
import { omit, pick } from 'lodash-es'
withDefaults(
	defineProps<{
		data: { [key: string]: any }
		formItem: FormItemProps
		table: boolean
		prop: string
	}>(),
	{ table: () => true, forms: () => [] }
)
</script>

<style lang="scss" scoped>
.table-item {
	&.el-form-item--small {
		:deep(.el-form-item__label) {
			margin-left: -7px;
		}
	}
	:deep(.el-form-item__label) {
		position: absolute;
		margin-left: -10px;
	}
	:deep(.el-form-item__content) {
		.el-form-item__error {
			position: unset;
		}
	}
}
</style>
