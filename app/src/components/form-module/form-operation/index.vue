<template>
	<el-form-item class="form-operation">
		<template v-for="btn in btns">
			<slot v-if="btn.slot" :name="btn.slot"></slot>
			<el-button v-else v-bind="omit(btn, 'label')">
				{{ btn.label }}
			</el-button>
		</template>
	</el-form-item>
</template>

<script setup lang="ts">
import { omit } from 'lodash-es'

interface Btn {
	label: string
	slot?: string
	[key: string]: any
}
defineProps<{
	btns: Btn[]
}>()
</script>

<style lang="scss" scoped></style>
