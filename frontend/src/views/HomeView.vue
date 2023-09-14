<template>
    <BasicPage dense>
        <div class="d-flex align-center justify-center">
            Welcome to the MediaManager admin app. To get started, check out the navigation menu on the left.
        </div>
    </BasicPage>
</template>

<script setup lang="ts">
import BasicPage from "@/components/global/BasicPage.vue"
import { useRouter } from "vue-router";

const router = useRouter();

// Since this is a catch-all page, we make sure the url is correct
router.push("/");
</script>
