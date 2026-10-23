<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '../stores/cart'
import { useAuth } from '../stores/auth'
import { lang, setLang, t } from '../i18n'
import mark from '../assets/logo-mark.png'
import { api } from '../api'

const cart = useCart()
const auth = useAuth()
const router = useRouter()
const q = ref('')
const open = ref(false)

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
      <nav :class="{ open }" @click="open = false">
        <RouterLink to="/">{{ t('Home') }}</RouterLink>
        <RouterLink to="/shop">{{ t('Shop') }}</RouterLink>
        <RouterLink to="/blog">{{ t('Blog') }}</RouterLink>
        <RouterLink to="/about">{{ t('About us') }}</RouterLink>
        <RouterLink to="/contact">{{ t('Contact') }}</RouterLink>
        <a v-if="auth.user?.is_staff" href="/admin/" class="admin-link" @click.prevent="openAdmin">{{ t('Admin') }}</a>
      </nav>
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
  </header>
</template>

<style scoped>
.top { position: sticky; top: 0; z-index: 10; background: var(--wine); color: var(--on-wine); }
.top::after { content: ''; display: block; height: 2px; background: var(--hem); }
.bar { display: flex; align-items: center; gap: 28px; min-height: 72px; flex-wrap: wrap; }
.logo { display: inline-flex; align-items: center; gap: 10px; font-family: var(--logo); font-size: 1.75rem; font-weight: 400; line-height: 1; color: var(--gold-light); }
.mark { width: 40px; height: 40px; background: var(--gold-light); -webkit-mask: var(--mark) center / contain no-repeat; mask: var(--mark) center / contain no-repeat; transition: transform .6s ease; }
.logo:hover .mark { transform: rotate(90deg); }
nav { display: flex; gap: 22px; }
nav a { color: rgba(248, 243, 241, .78); padding: 4px 0; border-bottom: 1.5px solid transparent; }
nav a:hover { color: var(--on-wine); }
nav a.router-link-exact-active { color: var(--on-wine); border-color: var(--gold-light); }
nav a.admin-link { color: var(--wine); background: var(--gold-light); padding: 2px 10px; border: 0; border-radius: var(--radius); font-size: .9rem; font-weight: 600; }
nav a.admin-link:hover { color: var(--wine-deep); }
.search { flex: 1; max-width: 300px; margin-left: auto; }
.search input { background: rgba(255, 255, 255, .1); border-color: rgba(248, 243, 241, .35); color: var(--on-wine); padding: 8px 14px; }
.search input::placeholder { color: rgba(248, 243, 241, .65); }
.search input:focus { background: rgba(255, 255, 255, .16); border-color: var(--gold-light); outline-color: var(--gold-light); }
.langs { display: flex; }
.langs button { border: 0; background: none; color: rgba(248, 243, 241, .65); font: inherit; font-size: .9rem; font-weight: 600; padding: 6px 7px; cursor: pointer; border-bottom: 1.5px solid transparent; }
.langs button:hover { color: var(--on-wine); }
.langs button.on { color: var(--gold-light); border-color: var(--gold-light); }
.top :focus-visible { outline-color: var(--gold-light); }
.cart { display: inline-flex; align-items: center; gap: 2px; }
.actions { display: flex; gap: 20px; align-items: center; }
.actions a:hover { color: var(--gold-light); }
.badge { background: var(--gold-light); color: var(--wine-deep); border-radius: 999px; font-size: .75rem; font-weight: 600; min-width: 20px; text-align: center; padding: 1px 6px; margin-left: 2px; }
.burger { display: none; background: none; border: 0; font-size: 1.5rem; color: inherit; margin-left: auto; cursor: pointer; }

@media (max-width: 900px) {
  .bar { gap: 10px 14px; min-height: 60px; padding-top: 8px; padding-bottom: 8px; }
  .logo { font-size: 1.5rem; order: 1; }
  .mark { width: 34px; height: 34px; }
  .actions { order: 2; margin-left: auto; gap: 14px; white-space: nowrap; }
  .burger { display: block; order: 3; margin-left: 0; padding: 4px 8px; min-width: 44px; min-height: 44px; }
  .search { order: 4; flex: 1 1 220px; min-width: 0; max-width: none; margin: 0; }
  .langs { order: 5; }
  nav { display: none; order: 6; width: 100%; flex-direction: column; gap: 0; padding-bottom: 6px; }
  nav a { padding: 12px 2px; border-bottom: 0; border-top: 1px solid rgba(248, 243, 241, .15); }
  nav a.router-link-exact-active { color: var(--gold-light); }
  nav a.admin-link { align-self: flex-start; margin: 8px 0 4px; padding: 6px 14px; }
  nav.open { display: flex; }
}
@media (max-width: 380px) {
  .actions { gap: 10px; font-size: .9rem; }
  .logo { font-size: 1.3rem; }
}
@media (prefers-reduced-motion: reduce) { .mark { transition: none; } }
</style>
