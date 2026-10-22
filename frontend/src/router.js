import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from './stores/auth'
import { lang, t } from './i18n'
import { watch } from 'vue'

const routes = [
  { path: '/', component: () => import('./views/HomeView.vue') },
  { path: '/shop', component: () => import('./views/ProductsView.vue'), meta: { title: 'Search' } },
  { path: '/category/:slug', component: () => import('./views/ProductsView.vue') },
  { path: '/product/:slug', component: () => import('./views/ProductView.vue') },
  { path: '/cart', component: () => import('./views/CartView.vue'), meta: { title: 'Cart' } },
  { path: '/checkout', component: () => import('./views/CheckoutView.vue'), meta: { title: 'Checkout' } },
  { path: '/payment/return', component: () => import('./views/PaymentReturnView.vue'), meta: { title: 'Payment' } },
  { path: '/order/done', component: () => import('./views/OrderDoneView.vue'), meta: { title: 'Thank you' } },
  { path: '/login', component: () => import('./views/AuthView.vue'), meta: { title: 'Sign in' } },
  { path: '/register', component: () => import('./views/AuthView.vue'), meta: { title: 'Create account' } },
  { path: '/account', component: () => import('./views/AccountView.vue'), meta: { title: 'My account', auth: true } },
  { path: '/blog', component: () => import('./views/BlogListView.vue'), meta: { title: 'Blog' } },
  { path: '/blog/:slug', component: () => import('./views/BlogView.vue') },
  { path: '/about', component: () => import('./views/PageView.vue'), props: { slug: 'about' } },
  { path: '/contact', component: () => import('./views/PageView.vue'), props: { slug: 'contact', form: true } },
  { path: '/:pathMatch(.*)*', component: () => import('./views/NotFoundView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: (to, from, saved) => saved || { top: 0 },
})

router.beforeEach(async (to) => {
  const auth = useAuth()
  if (!auth.ready) await auth.init()
  if (to.meta.auth && !auth.loggedIn) return { path: '/login', query: { next: to.fullPath } }
})

const setTitle = () => {
  const m = router.currentRoute.value.meta
  document.title = m.title ? `${t(m.title)} · Didostati` : 'Didostati'
}
router.afterEach(setTitle)
watch(lang, setTitle)

export default router
