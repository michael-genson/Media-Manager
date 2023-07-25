<template>
    <main>
        <v-card
            class="mx-auto pa-12 pb-8"
            :min-width="$vuetify.display.smAndDown ? undefined : 480"
            elevation="8"
            rounded="lg"
        >
            <v-card-title>
                <v-container>
                    <v-row no-gutters>
                        <v-col cols="2" class="d-flex justify-center align-center">
                            <v-icon icon="custom:logo" size="x-large" />
                        </v-col>
                        <v-col cols="10" class="d-flex justify-center align-center">
                            <h2 class="my-2">MediaManager</h2>
                        </v-col>
                    </v-row>
                </v-container>
            </v-card-title>
            <UserLogin v-model:loading="loading" @submit="handleSubmit" />
            <v-card-text v-if="errorMessage" class="text-danger text-h6 text-center pb-0">{{ errorMessage }}</v-card-text>
        </v-card>
    </main>
</template>


<script setup lang="ts">
import axios from "axios";
import UserLogin from "@/components/user/UserLogin.vue";
import type { LoginForm } from "@/components/user/UserLogin.vue";
import type { Token } from "@/types/mediamanager/users";
import { ref } from "vue";

const loading = ref(false);
const errorMessage = ref("");

async function handleSubmit(form: LoginForm) {
    loading.value = true;
    errorMessage.value = "";

    const formData = new FormData();
    formData.append("username", form.email);
    formData.append("password", form.password);

    try {
        const { data } = await axios.post<Token>("/api/authorization/token", formData);
        // TODO: advance to home page
        console.log(data);
    } catch(err) {
        loading.value = true;
        errorMessage.value = "Invalid Login";
    }
}
</script>
