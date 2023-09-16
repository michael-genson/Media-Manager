<template>
    <div v-if="appConfig && isReady">
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
                        <v-divider class="mt-0" />
                        <v-select
                            v-model="selectedLibraryChoices"
                            label="Monitored Libraries"
                            :items="allLibraryChoices"
                            item-title="sectionName"
                            multiple
                            chips
                        >
                        </v-select>
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
    </div>
    <div v-else class="mx-auto" style="width: fit-content;">
        <v-progress-circular indeterminate color="primary" :size="128" :width="6" />
    </div>
    <v-snackbar v-model="showSuccess" timeout="5000" color="success" location="top">
        <div class="text-center">App Config successfully updated</div>
    </v-snackbar>
    <v-snackbar v-model="showFail" timeout="5000" color="danger" location="top">
        <div class="text-center text-white">Oops, something went wrong</div>
    </v-snackbar>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

import { useAppConfig } from "@/services/use-app-config";
import { useDisplay } from "vuetify";
import type { TautulliLibrary } from "@/types/mediamanager/expired-media";


const { actions: appConfigActions, appConfig, allLibraryChoices, selectedLibraryChoices } = useAppConfig();
const display = useDisplay();

const formIsValid = ref(false);
const isLoading = ref(true);
const isReady = ref(false);
const isMobile = ref(display.smAndDown);

const showFail = computed(() => !isLoading.value && !appConfig.value);
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

async function handleSubmit() {
    if (!appConfig.value) {
        return;
    }

    isLoading.value = true;

    // populate monitoredLibraryIds
    const libraryChoicesByName = new Map<string, TautulliLibrary>();
        allLibraryChoices.value.forEach((choice) => {
        libraryChoicesByName.set(choice.sectionName, choice);
    })

    if (selectedLibraryChoices.value?.length) {
        const chosenIds: string[] = [];
        selectedLibraryChoices.value.forEach((choice) => {
            const choiceId = libraryChoicesByName.get(choice)?.sectionId;
            if (choiceId) {
                chosenIds.push(choiceId);
            };
        });

        appConfig.value.monitoredLibraryIds = chosenIds;
    } else {
        appConfig.value.monitoredLibraryIds = [];
    }

    await appConfigActions.update(appConfig.value);
    if (appConfig.value) {
        showSuccess.value = true;
    }

    isLoading.value = false;
}

watch([isReady, () => appConfig.value, () => allLibraryChoices.value], ([isReadyVal, configVal, choicesVal]) => {
    if (configVal && choicesVal.length) {
        if (!isReadyVal) {
            isReady.value = true;
            isLoading.value = false;
        }
    }
});
</script>
