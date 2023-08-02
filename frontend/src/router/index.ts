import { createRouter, createWebHistory } from "vue-router"
import HomeView from "@/views/HomeView.vue";
import AppSettingsView from "@/views/AppSettingsView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/settings",
      name: "app settings",
      component: AppSettingsView,
    },
    { // 404
      path: "/:pathMatch(.*)*",
      component: HomeView,
    },
  ]
})

export default router
