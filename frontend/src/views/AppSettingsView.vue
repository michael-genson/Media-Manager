<template>
    <main :class="attrs.class.main" style="width: 100%;">
        <v-card
            :class="attrs.class.card"
            :min-width="$vuetify.display.smAndDown ? undefined : 480"
            :width="$vuetify.display.smAndDown ? '100%' : '80%'"
            elevation="8"
            rounded="lg"
        >
            <v-card-title class="d-flex justify-center align-center py-0 mb-2">
                <h2>App Config</h2>
            </v-card-title>
            <v-divider />
            <AppConfigForm />
        </v-card>
    </main>
</template>

<script setup lang="ts">
import AppConfigForm from "@/components/app/settings/AppConfigForm.vue"
import { computed, ref } from "vue";
import { useDisplay } from "vuetify";

const display = useDisplay();
const isMobile = ref(display.smAndDown);

const attrs = computed( () => {
    return isMobile.value ? {
        class: {
            main: "px-0 py-1",
            card: "my-4 mx-auto px-2 pt-2 pb-8",
        }
    } : {
        class: {
            main: "px-12 py-2",
            card: "my-4 mx-auto px-12 pt-2 pb-8",
        },
    };
});
</script>
