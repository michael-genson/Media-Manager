<template>
    <main :class="attrs.class.main" style="width: 100%;">
        <v-card
            :class="dense ? 'pa-4 ma-auto' : attrs.class.card"
            :min-width="$vuetify.display.smAndDown ? undefined : 480"
            :width="dense ? 'fit-content' : $vuetify.display.smAndDown ? '100%' : '80%'"
            elevation="8"
            rounded="lg"
        >
            <v-card-title :class="dense ? 'd-flex justify-center align-center pa-0 ma-0' : attrs.class.title">
                <h2 v-if="title">{{ title }}</h2>
            </v-card-title>
            <v-divider v-if="title" />
            <slot></slot>
        </v-card>
    </main>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useDisplay } from "vuetify";

defineProps({
    title: {
        type: String,
        default: undefined,
    },
    dense: {
        type: Boolean,
        default: false,
    },
});

const display = useDisplay();
const isMobile = ref(display.smAndDown);

const attrs = computed( () => {
    return isMobile.value ? {
        class: {
            main: "px-0 py-1",
            card: "my-4 mx-auto px-2 pt-2 pb-8",
            title: "d-flex justify-center align-center py-0 mb-2",
        }
    } : {
        class: {
            main: "px-12 py-2",
            card: "my-4 mx-auto px-12 pt-2 pb-8",
            title: "d-flex justify-center align-center py-0 mb-2",
        },
    };
});
</script>
