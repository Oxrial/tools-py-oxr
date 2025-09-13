<template>
	<el-form :model="data">
		<template v-for="formItem in forms" :key="index">
			<EditFormItem :data="data" :formItem="formItem" :form="form" />
		</template>
	</el-form>
</template>

<script setup lang="ts">
import type { FormInstance } from 'element-plus'
import EditFormItem from '../edit-form-item/index.vue'
withDefaults(
	defineProps<{
		data: { [key: string]: any }
		forms: any[]
		form: FormInstance
	}>(),
	{}
)
</script>

<style lang="scss" scoped></style>
