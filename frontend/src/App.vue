<template>
    <v-app>
        <div v-if="!isLoading">
            <!-- Main App -->
            <div v-if="user && !user.isDefaultUser">
                <v-app-bar
                    color="primary"
                >
                    <v-app-bar-nav-icon @click.stop="toggleNav = !toggleNav" />
                    <v-toolbar-title style="cursor: pointer" @click.stop="$router.push('/')">MediaManager</v-toolbar-title>
                    <v-spacer />
                    <template v-slot:append>
                        <v-btn prepend-icon="mdi-logout" :text="$vuetify.display.smAndDown ? undefined : 'Log Out'" @click.stop="handleLogout" />
                    </template>
                </v-app-bar>
                <v-navigation-drawer
                    v-model="toggleNav"
                    expand-on-hover
                    rail
                    width="300"
                >
                    <v-list density="compact">
                        <v-list-item
                            prepend-icon="mdi-account-circle"
                            title="User"
                            :subtitle="user.email"
                        />
                        <v-divider />
                        <v-list-item to="/" prepend-icon="custom:logo" title="Home" />
                        <!-- Log Out -->
                        <v-list-item prepend-icon="mdi-logout" title="Log Out" class="fixedBottom" @click.stop="handleLogout" />
                    </v-list>
                    <template v-slot:append>
                    </template>
                </v-navigation-drawer>
                <v-main class="d-flex align-center justify-center" style="min-height: 300px;">
                    <router-view />
                </v-main>
            </div>
            <div v-else>
                <!-- Login and Default User forms -->
                <v-main class="d-flex align-center justify-center" style="height: 100vh;">
                    <v-card
                        class="ma-auto pa-12 pb-8"
                        :min-width="$vuetify.display.smAndDown ? undefined : 480"
                        max-width="fit-content"
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
                                <v-row v-if="user && user.isDefaultUser" no-gutters class="my-2">
                                    <v-col class="d-flex justify-center align-center">
                                        <p style="text-align: center;">Please replace the default<br />login credentials before continuing</p>
                                    </v-col>
                                </v-row>
                            </v-container>
                        </v-card-title>
                        <ChangeDefaultUserForm v-if="user && user.isDefaultUser" @changedUser="handleLogin" />
                        <UserLoginForm v-else @loggedIn="handleLogin" />
                    </v-card>
                </v-main>
            </div>
        </div>
    </v-app>
</template>

<script setup lang="ts">
import UserLoginForm from "@/components/user/UserLoginForm.vue";
import { useCookies } from "@vueuse/integrations/useCookies";
import { access_token_cookie, useApi } from "@/services/backend/client";
import type { User } from "@/types/mediamanager/users";
import {  ref } from "vue";
import ChangeDefaultUserForm from "./components/user/ChangeDefaultUserForm.vue";
import { useDisplay } from "vuetify";

const api = useApi();
const cookies = useCookies();
const display = useDisplay();

const isMobile = ref(!display.smAndDown.value);
const toggleNav = ref(isMobile);

const isLoading = ref(true);
const user = ref<User|null>(null);

if (cookies.get(access_token_cookie)) {
    logInUser().then(() => isLoading.value = false);
}
else {
    isLoading.value = false;
}

async function logInUser() {
    const { data } = await api.get<User>("/api/authorization/me");
    user.value = data;

    if (!user.value) {
        cookies.remove(access_token_cookie);
    }
}

async function handleLogin() {
    window.location.reload();
}

async function handleLogout() {
    cookies.remove(access_token_cookie);
    window.location.reload();
}

</script>

<style lang="css">
.fixedBottom {
    position: fixed !important;
    bottom: 0 !important;
    width: 100%;
}
</style>
