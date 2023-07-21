import 'bootstrap/dist/css/bootstrap.css';
import './assets/main.css'
import { createApp } from 'vue'
import axios from 'axios';

import App from './App.vue'
import router from './router'

const app = createApp(App)

axios.defaults.withCredentials = true;
axios.defaults.baseURL = 'http://localhost:9000/';

app.use(router)
app.mount('#app')
