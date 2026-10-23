import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from './stores/auth'
import { lang, setLang, stripLang, t, withLang } from './i18n'
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
  // Every page also exists under /ka for Georgian; the catch-all already matches both.
  routes: routes.flatMap((r) => (r.path.startsWith('/:') ? [r] : [{ ...r, path: withLang(r.path, 'ka') }, r])),
  scrollBehavior: (to, from, saved) => saved || { top: 0 },
})

// Links in the code are written without the prefix: give them the one of the current language,
// so hrefs (what search engines follow) and active-link highlighting are right.
const resolve = router.resolve.bind(router)
router.resolve = (to, current) => {
  if (typeof to === 'string' && to.startsWith('/')) to = withLang(to)
  else if (to?.path?.startsWith('/')) to = { ...to, path: withLang(to.path) }
  return resolve(to, current)
}

router.beforeEach(async (to) => {
  // The address decides the language; an unprefixed address while browsing in Georgian gets the prefix.
  if (stripLang(to.path) !== to.path) {
    if (lang.value !== 'ka') setLang('ka')
  } else if (lang.value === 'ka') {
    return withLang(to.fullPath)
  }
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
// Switching language moves to the same page in that language.
watch(lang, (code) => {
  const { fullPath } = router.currentRoute.value
  if (withLang(fullPath, code) !== fullPath) router.replace(withLang(fullPath, code))
})

export default router
