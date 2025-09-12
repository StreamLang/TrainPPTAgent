import { createRouter, createWebHistory } from 'vue-router'
import Editor from '../views/Editor/index.vue'
import Outline from '../views/Outline/index.vue'
import PPT from '../views/PPT/index.vue'
import Screen from '../views/Screen/index.vue'



const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home/index.vue'),
  },
  {
    path: '/outline',
    name: 'Outline',
    component: Outline,
  },
  {
    path: '/editor',
    name: 'Editor',
    component: Editor,
  },
  {
    path: '/ppt',
    name: 'PPT',
    component: PPT,
  },
  {
    path: '/screen',
    name: 'Screen',
    component: Screen,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router