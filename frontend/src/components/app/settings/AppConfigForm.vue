<template>
    <v-form v-model="formIsValid" @submit.prevent="handleSubmit">
        <v-container class="mb-4 pa-0 d-flex flex-wrap justify-center">
            <v-card :class="attrs.class.card" :style="attrs.style.card">
                <v-card-title>Ombi</v-card-title>
                <v-card-text>
                    <v-text-field
                        v-model="appConfig.ombiUrl"
                        label="URL"
                        placeholder="https://your-ombi-url.com"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.ombiApiKey"
                        label="API Key"
                        type="password"
                        density="compact"
                    />
                </v-card-text>
            </v-card>
            <v-card :class="attrs.class.card" :style="attrs.style.card">
                <v-card-title>qBittorrent</v-card-title>
                <v-card-text>
                    <v-text-field
                        v-model="appConfig.qbittorrentUrl"
                        label="URL"
                        placeholder="https://your-qbittorrent-url.com"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.qbittorrentUsername"
                        label="Username"
                        placeholder="admin"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.qbittorrentPassword"
                        label="Password"
                        type="password"
                        density="compact"
                    />
                </v-card-text>
            </v-card>
            <v-card :class="attrs.class.card" :style="attrs.style.card">
                <v-card-title>Tautulli</v-card-title>
                <v-card-text>
                    <v-text-field
                        v-model="appConfig.tautulliUrl"
                        label="URL"
                        placeholder="https://your-tautulli-url.com"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.tautulliApiKey"
                        label="API Key"
                        type="password"
                        density="compact"
                    />
                </v-card-text>
            </v-card>
            <v-card :class="attrs.class.card" :style="attrs.style.card">
                <v-card-title>Radarr</v-card-title>
                <v-card-text>
                    <v-text-field
                        v-model="appConfig.radarrUrl"
                        label="URL"
                        placeholder="https://your-radarr-url.com"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.radarrApiKey"
                        label="API Key"
                        type="password"
                        density="compact"
                    />
                </v-card-text>
            </v-card>
            <v-card :class="attrs.class.card" :style="attrs.style.card">
                <v-card-title>Sonarr</v-card-title>
                <v-card-text>
                    <v-text-field
                        v-model="appConfig.sonarrUrl"
                        label="URL"
                        placeholder="https://your-sonarr-url.com"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.sonarrApiKey"
                        label="API Key"
                        type="password"
                        density="compact"
                    />
                </v-card-text>
            </v-card>
            <v-card :class="attrs.class.card" :style="attrs.style.card">
                <v-card-title>SMTP</v-card-title>
                <v-card-text>
                    <v-text-field
                        v-model="appConfig.smtpServer"
                        label="Server"
                        placeholder="smtp.gmail.com"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.smtpPort"
                        label="Port"
                        type="number"
                        placeholder="587"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.smtpSender"
                        label="Sender"
                        placeholder="smtp.gmail.com"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.smtpUsername"
                        label="Username"
                        placeholder="smtp.gmail.com"
                        density="compact"
                    />
                    <v-text-field
                        v-model="appConfig.smtpPassword"
                        label="Password"
                        type="password"
                        density="compact"
                    />
                </v-card-text>
            </v-card>
        </v-container>
        <!-- Submit -->
        <v-btn
            block
            color="primary"
            type="submit"
            size="large"
            variant="tonal"
        >
            <v-progress-circular v-if="isLoading" indeterminate color="primary" />
            <div v-if="!isLoading">Submit</div>
        </v-btn>
    </v-form>

    <v-snackbar v-model="showSuccess" timeout="5000" color="success" location="top">
        <div class="text-center">App Config successfully updated</div>
    </v-snackbar>
    <v-snackbar v-model="showFail" timeout="5000" color="danger" location="top">
        <div class="text-center">Oops, something went wrong</div>
    </v-snackbar>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

import { useApi } from "@/services/backend/client";
import type { AppConfig } from "@/types/mediamanager/app";
import { useDisplay } from "vuetify";

const emit = defineEmits(["isReady"]);
const display = useDisplay();

const api = useApi();
const appConfig = ref<AppConfig>({});
const formIsValid = ref(false);
const isLoading = ref(true);
const isMobile = ref(display.smAndDown);

const showFail = ref(false);
const showSuccess = ref(false);

const attrs = computed(() => {
    return isMobile.value ? {
        class: {
            card: "mx-4 my-2 elevation-8",
        },
        style: {
            card: "width: 100%;"
        },
    } : {
        class: {
            card: "mx-4 my-2 elevation-8",
        },
        style: {
            card: "width: 400px;"
        },
    }
})

async function refreshConfig() {
    const { data } = await api.get<AppConfig>("/api/config")
    if (!data) {
        showFail.value = true;
        return;
    }

    appConfig.value = data;
}

async function handleSubmit() {
    isLoading.value = true;
    const { data } = await api.put<AppConfig>("/api/config", appConfig.value);
    if (data) {
        appConfig.value = data;
        showSuccess.value = true;
    }
    else {
        showFail.value = true;
    }
    isLoading.value = false;
}

refreshConfig().then( () => { isLoading.value = false; emit("isReady"); })
</script>