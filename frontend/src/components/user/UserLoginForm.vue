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
            <v-progress-circular v-if="loading" indeterminate color="primary" />
            <div v-if="!loading">Log In</div>
        </v-btn>
        <v-card-text v-if="errorMessage" class="text-danger text-h6 text-center pb-0">{{ errorMessage }}</v-card-text>
    </v-form>
</template>

<script setup lang="ts">
import { access_token_cookie, useApi } from "@/services/backend/client";
import type { Token } from "@/types/mediamanager/users";
import { reactive, ref } from "vue";
import { useCookies } from "@vueuse/integrations/useCookies";
const emit = defineEmits(["loggedIn"])

const loading = ref(false);
const errorMessage = ref("");
const visible = ref(false);

const api = useApi();
const cookies = useCookies();

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

async function handleSubmit() {
    if (!formIsValid.value) {
        return;
    }

    loading.value = true;
    errorMessage.value = "";

    const formData = new FormData();
    formData.append("username", form.email);
    formData.append("password", form.password);

    const { data } = await api.post<Token>("/api/authorization/token", formData);
    if (!data) {
        loading.value = false;
        errorMessage.value = "Invalid Login";
        return;
    }

    cookies.set(access_token_cookie, `${data.token_type || "Bearer"} ${data.access_token}`)
    console.log(cookies.get(access_token_cookie));
    emit("loggedIn");
}
</script>

<script lang="ts">
export type LoginForm = {
    email: string;
    password: string;
};
</script>
