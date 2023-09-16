import { createRouter, createWebHistory } from "vue-router"
import HomeView from "@/views/HomeView.vue";
import SchedulerView from "@/views/SchedulerView.vue";
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
      path: "/scheduler",
      name: "app scheduler",
      component: SchedulerView,
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
