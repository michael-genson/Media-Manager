<template>
    <v-form v-model="formIsValid" @submit.prevent="handleSubmit">
        <v-text-field
            v-model="form.email"
            name="email"
            label="Email"
            clearable
            type="email"
            :rules="[validations.required, validations.isEmail]"
            placeholder="Email address"
            density="compact"
            prepend-inner-icon="mdi-email-outline"
            variant="outlined"
            class="mb-2"
        />
        <v-text-field
            v-model="form.password"
            :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
            name="password"
            label="Password"
            clearable
            :type="visible ? 'text' : 'password'"
            :rules="[validations.required]"
            density="compact"
            placeholder="Enter your password"
            prepend-inner-icon="mdi-lock-outline"
            variant="outlined"
            class="mb-2"
            @click:append-inner="visible = !visible"
        />
        <v-btn
            block
            color="primary"
            type="submit"
            size="large"
            variant="tonal"
        >
            <v-progress-circular v-if="props.loading" indeterminate color="primary" />
            <div v-if="!props.loading">Log In</div>
        </v-btn>
    </v-form>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";

const props = defineProps({
    loading: { type: Boolean, default: false }
})
const emit = defineEmits(["submit"])

const visible = ref(false);

const formIsValid = ref(false);
const form = reactive<LoginForm>({
    email: "",
    password: "",
})

const emailRegex = /^\S+@\S+$/
const validations = {
    required: (val: string) => !!val || "Field is required",
    isEmail: (val: string) => emailRegex.test(val) || "Invalid email",
}

const handleSubmit = () => {
    if (formIsValid.value) {
        emit("submit", form);
    }
}
</script>

<script lang="ts">
export type LoginForm = {
    email: string;
    password: string;
};
</script>
