<template>
    <div v-if="isReady">
    </div>
    <div v-else class="mx-auto" style="width: fit-content;">
        <v-progress-circular indeterminate color="primary" :size="128" :width="6" />
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const isReady = ref(false);

</script>
