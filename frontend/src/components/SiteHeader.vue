<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCart } from '../stores/cart'
import { useAuth } from '../stores/auth'
import { lang, setLang, stripLang, t } from '../i18n'
import mark from '../assets/logo-mark.png'
import { api } from '../api'

const cart = useCart()
const auth = useAuth()
const router = useRouter()
const route = useRoute()
const q = ref('')
const open = ref(false)
// Pages from the admin (About us, Contact...), each with its submenu.
const pages = ref([])
watch(lang, () => api('/pages/').then((p) => (pages.value = p)).catch(() => {}), { immediate: true })

const isCurrent = (page) => page.children.some((c) => c.path === stripLang(route.path))

// Also drop focus, or a submenu opened with the keyboard/mouse stays open after its link is followed.
function closeMenu() {
  open.value = false
  document.activeElement?.blur()
}

function search() {
  router.push({ path: '/shop', query: q.value.trim() ? { search: q.value.trim() } : {} })
  open.value = false
}

// The admin uses a session cookie, not our bearer token: create the session first so no second login is needed.
async function openAdmin() {
  await api('/auth/admin-session/', { method: 'POST' }).catch(() => {})
  window.location.href = '/admin/'
}
</script>

<template>
  <header class="top">
    <div class="wrap bar">
      <RouterLink to="/" class="logo" :style="{ '--mark': `url(${mark})` }">
        <span class="mark" aria-hidden="true"></span>{{ lang === 'ka' ? 'დიდოსტატი' : 'Didostati' }}
      </RouterLink>
      <button class="burger" :aria-label="t('Menu')" :aria-expanded="open" @click="open = !open">☰</button>
      <form class="search" @submit.prevent="search">
        <input v-model="q" type="search" :placeholder="t('Search products…')" :aria-label="t('Search products')" />
      </form>
      <div class="langs">
        <button :class="{ on: lang === 'en' }" :aria-pressed="lang === 'en'" lang="en" title="English" @click="setLang('en')">EN</button>
        <button :class="{ on: lang === 'ka' }" :aria-pressed="lang === 'ka'" lang="ka" title="ქართული" @click="setLang('ka')">ქა</button>
      </div>
      <div class="actions">
        <RouterLink v-if="auth.loggedIn" to="/account">{{ auth.user.first_name || t('Account') }}</RouterLink>
        <RouterLink v-else to="/login">{{ t('Sign in') }}</RouterLink>
        <RouterLink to="/cart" class="cart" :aria-label="t('Cart')" :title="t('Cart')">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/></svg>
          <span v-if="cart.count" class="badge">{{ cart.count }}</span>
        </RouterLink>
      </div>
    </div>
    <div class="menu" :class="{ open }">
      <nav class="wrap" @click="closeMenu">
        <RouterLink to="/">{{ t('Home') }}</RouterLink>
        <RouterLink to="/shop">{{ t('Shop') }}</RouterLink>
        <RouterLink to="/blog">{{ t('Blog') }}</RouterLink>
        <div v-for="page in pages" :key="page.slug" class="item" :class="{ 'has-sub': page.children.length }">
          <RouterLink :to="page.path" :class="{ current: isCurrent(page) }" :aria-haspopup="page.children.length ? 'true' : undefined">{{ page.title }}</RouterLink>
          <div v-if="page.children.length" class="sub">
            <RouterLink v-for="child in page.children" :key="child.slug" :to="child.path">{{ child.title }}</RouterLink>
          </div>
        </div>
        <a v-if="auth.user?.is_staff" href="/admin/" class="admin-link" @click.prevent="openAdmin">{{ t('Admin') }}</a>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.top { position: sticky; top: 0; z-index: 10; background: var(--wine); color: var(--on-wine); }
.top::after { content: ''; display: block; height: 2px; background: var(--hem); }
.bar { display: flex; align-items: center; gap: 24px; min-height: 68px; }
.logo { display: inline-flex; align-items: center; gap: 10px; font-family: var(--logo); font-size: 1.75rem; font-weight: 400; line-height: 1; color: var(--gold-light); white-space: nowrap; }
.mark { width: 40px; height: 40px; background: var(--gold-light); -webkit-mask: var(--mark) center / contain no-repeat; mask: var(--mark) center / contain no-repeat; transition: transform .6s ease; }
.logo:hover .mark { transform: rotate(90deg); }
.search { flex: 1; max-width: 460px; margin: 0 auto; }
.search input { background: rgba(255, 255, 255, .1); border-color: rgba(248, 243, 241, .35); color: var(--on-wine); padding: 8px 14px; }
.search input::placeholder { color: rgba(248, 243, 241, .65); }
.search input:focus { background: rgba(255, 255, 255, .16); border-color: var(--gold-light); outline-color: var(--gold-light); }
.langs { display: flex; }
.langs button { border: 0; background: none; color: rgba(248, 243, 241, .65); font: inherit; font-size: .9rem; font-weight: 600; padding: 6px 7px; cursor: pointer; border-bottom: 1.5px solid transparent; }
.langs button:hover { color: var(--on-wine); }
.langs button.on { color: var(--gold-light); border-color: var(--gold-light); }
.top :focus-visible { outline-color: var(--gold-light); }
.cart { display: inline-flex; align-items: center; gap: 2px; }
.actions { display: flex; gap: 20px; align-items: center; white-space: nowrap; }
.actions a:hover { color: var(--gold-light); }
.badge { background: var(--gold-light); color: var(--wine-deep); border-radius: 999px; font-size: .75rem; font-weight: 600; min-width: 20px; text-align: center; padding: 1px 6px; margin-left: 2px; }
.burger { display: none; background: none; border: 0; font-size: 1.5rem; color: inherit; margin-left: auto; cursor: pointer; }

/* Second row: the page menu, with a submenu under pages that have subpages. */
.menu { border-top: 1px solid rgba(248, 243, 241, .12); }
nav { display: flex; align-items: center; gap: 4px 28px; flex-wrap: wrap; }
nav a { display: block; color: rgba(248, 243, 241, .78); padding: 10px 0 9px; border-bottom: 1.5px solid transparent; white-space: nowrap; }
nav a:hover { color: var(--on-wine); }
nav a.router-link-exact-active, nav a.current { color: var(--on-wine); border-color: var(--gold-light); }
.item { position: relative; }
.has-sub > a::after { content: ''; display: inline-block; width: 6px; height: 6px; margin: 0 2px 3px 8px; border: solid currentColor; border-width: 0 1.5px 1.5px 0; transform: rotate(45deg); opacity: .7; }
.sub { display: none; position: absolute; top: 100%; left: -16px; min-width: 210px; padding: 6px 0; background: var(--wine-deep); border-top: 2px solid var(--gold-light); border-radius: 0 0 var(--radius) var(--radius); box-shadow: 0 10px 24px rgba(43, 26, 33, .28); }
.item:hover .sub, .item:focus-within .sub { display: block; }
.sub a { padding: 9px 16px; border: 0; }
.sub a:hover, .sub a.router-link-exact-active { color: var(--gold-light); background: rgba(255, 255, 255, .06); }
nav a.admin-link { margin-left: auto; color: var(--wine); background: var(--gold-light); padding: 2px 10px; border: 0; border-radius: var(--radius); font-size: .9rem; font-weight: 600; }
nav a.admin-link:hover { color: var(--wine-deep); }

@media (max-width: 900px) {
  .bar { flex-wrap: wrap; gap: 10px 14px; min-height: 60px; padding-top: 8px; padding-bottom: 8px; }
  .logo { font-size: 1.5rem; order: 1; }
  .mark { width: 34px; height: 34px; }
  .actions { order: 2; margin-left: auto; gap: 14px; }
  .burger { display: block; order: 3; margin-left: 0; padding: 4px 8px; min-width: 44px; min-height: 44px; }
  .search { order: 4; flex: 1 1 220px; min-width: 0; max-width: none; margin: 0; }
  .langs { order: 5; }
  .menu { display: none; }
  .menu.open { display: block; }
  nav { flex-direction: column; align-items: stretch; gap: 0; padding-bottom: 6px; }
  nav a { padding: 12px 2px; border-bottom: 0; border-top: 1px solid rgba(248, 243, 241, .15); }
  nav > a:first-child { border-top: 0; }
  nav a.router-link-exact-active, nav a.current { color: var(--gold-light); }
  .has-sub > a::after { display: none; }
  .sub { display: block; position: static; min-width: 0; padding: 0 0 0 18px; background: none; border: 0; box-shadow: none; }
  .sub a { padding: 10px 2px; border-top: 1px solid rgba(248, 243, 241, .1); font-size: .95rem; }
  .sub a:hover, .sub a.router-link-exact-active { background: none; }
  nav a.admin-link { align-self: flex-start; margin: 8px 0 4px; padding: 6px 14px; }
}
@media (max-width: 380px) {
  .actions { gap: 10px; font-size: .9rem; }
  .logo { font-size: 1.3rem; }
}
@media (prefers-reduced-motion: reduce) { .mark { transition: none; } }
</style>
