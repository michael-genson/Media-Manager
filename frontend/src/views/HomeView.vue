<template>
    <main class="d-flex align-center justify-center" style="width: 100%">
        <v-card
            class="ma-auto"
            width="fit-content"
            elevation="8"
            rounded
        >
            <template v-slot:text>
                <div>Welcome to the MediaManager admin app. To get started, check out the navigation menu on the left.</div>
            </template>
        </v-card>
    </main>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

// Since this is a catch-all page, we make sure the url is correct
router.push("/");
</script>
