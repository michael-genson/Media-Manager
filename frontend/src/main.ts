import "bootstrap/dist/css/bootstrap.css";
import "./assets/main.css"
import { createApp } from "vue"
import axios from "axios";

import "vuetify/styles"
import "@mdi/font/css/materialdesignicons.css"
import { createVuetify } from "vuetify"
import type { ThemeDefinition } from "vuetify"
import { aliases, mdi } from "vuetify/iconsets/mdi"
import { customIcons } from "@/assets/icons/customIcons";
import * as components from "vuetify/components"
import * as directives from "vuetify/directives"

import App from "./App.vue"
import router from "./router"

const app = createApp(App)

// Axios
axios.defaults.withCredentials = true;
axios.defaults.baseURL = process.env.API_URL || "http://localhost:9000/";

// Vuetify
const defaultTheme: ThemeDefinition = {
    dark: true,
    colors: {
        primary: "#00AE9C",
        secondary: "#66A8AE",
    },
}

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: "mdi",
        aliases,
        sets: {
            mdi,
            custom: customIcons,
        }
    },
    theme: {
        defaultTheme: "defaultTheme",
        themes: {
        defaultTheme,
        }
    },
})

app.use(vuetify)

app.use(router)
app.mount("#app")
