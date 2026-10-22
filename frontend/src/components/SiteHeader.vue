<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '../stores/cart'
import { useAuth } from '../stores/auth'
import { lang, setLang, t } from '../i18n'
import logo from '../assets/logo.jpg'
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
      <RouterLink to="/" class="logo"><img :src="logo" alt="didostati logo" class="logo-img" />Didostati</RouterLink>
      <button class="burger" :aria-label="t('Menu')" @click="open = !open">☰</button>
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
        <button :class="{ on: lang === 'en' }" aria-label="English" title="English" @click="setLang('en')">
          <svg viewBox="0 0 60 30" width="24" height="12" aria-hidden="true">
            <rect width="60" height="30" fill="#012169"/>
            <path d="M0 0l60 30M60 0L0 30" stroke="#fff" stroke-width="6"/>
            <path d="M0 0l60 30M60 0L0 30" stroke="#C8102E" stroke-width="2"/>
            <path d="M30 0v30M0 15h60" stroke="#fff" stroke-width="10"/>
            <path d="M30 0v30M0 15h60" stroke="#C8102E" stroke-width="6"/>
          </svg>
        </button>
        <button :class="{ on: lang === 'ka' }" aria-label="ქართული" title="ქართული" @click="setLang('ka')">
          <svg viewBox="0 0 30 20" width="24" height="16" aria-hidden="true">
            <rect width="30" height="20" fill="#fff"/>
            <path d="M12 0h6v20h-6zM0 7h30v6H0z" fill="#FF0000"/>
            <g fill="#FF0000">
              <path id="kc" d="M4.5 2.5h1v1h1v1h-1v1h-1v-1h-1v-1h1z"/>
              <use href="#kc" x="17"/><use href="#kc" y="11"/><use href="#kc" x="17" y="11"/>
            </g>
          </svg>
        </button>
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
.top { position: sticky; top: 0; z-index: 10; background: var(--card); border-bottom: 1px solid var(--line); }
.bar { display: flex; align-items: center; gap: 22px; min-height: 64px; flex-wrap: wrap; }
.logo { display: inline-flex; align-items: center; gap: .5rem; font-size: 1.5rem; font-weight: 800; letter-spacing: -.02em; color: var(--accent); }
nav { display: flex; gap: 18px; }
nav a { color: var(--muted); font-weight: 500; }
nav a:hover, nav a.router-link-exact-active { color: var(--ink); }
nav a.admin-link { color: #fff; background: var(--accent); padding: 4px 12px; border-radius: 999px; font-size: .9rem; }
nav a.admin-link:hover { color: #fff; opacity: .85; }
.search { flex: 1; max-width: 320px; margin-left: auto; }
.search input { border-radius: 999px; padding: 8px 16px; }
.langs { display: flex; gap: 2px; border: 1px solid var(--line); border-radius: 999px; padding: 2px; }
.langs button { border: 0; background: none; padding: 5px 8px; border-radius: 999px; cursor: pointer; display: inline-flex; align-items: center; opacity: .55; }
.langs button svg { border-radius: 2px; box-shadow: 0 0 0 1px var(--line); }
.langs button.on { background: var(--line); opacity: 1; }
.cart { display: inline-flex; align-items: center; gap: 2px; }
.actions { display: flex; gap: 18px; align-items: center; font-weight: 500; }
.badge { background: var(--accent); color: #fff; border-radius: 999px; font-size: .75rem; padding: 2px 7px; margin-left: 2px; }
.burger { display: none; background: none; border: 0; font-size: 1.5rem; color: inherit; margin-left: auto; cursor: pointer; }
.logo-img { height: 1.8em; width: auto; border-radius: 20%}

@media (max-width: 820px) {
  .bar { gap: 10px 12px; min-height: 56px; padding-top: 8px; padding-bottom: 8px; }
  .logo { font-size: 1.3rem; order: 1; }
  .actions { order: 2; margin-left: auto; gap: 14px; white-space: nowrap; }
  .burger { display: block; order: 3; margin-left: 0; padding: 4px 8px; min-width: 44px; min-height: 44px; }
  .search { order: 4; flex: 1 1 0; min-width: 0; max-width: none; margin: 0; }
  .langs { order: 5; }
  nav { display: none; order: 6; width: 100%; flex-direction: column; gap: 0; padding-bottom: 6px; }
  nav a { padding: 11px 4px; border-top: 1px solid var(--line); }
  nav a.admin-link { align-self: flex-start; margin: 8px 0 4px; padding: 6px 14px; }
  nav.open { display: flex; }
}
@media (max-width: 380px) {
  .actions { gap: 10px; font-size: .9rem; }
  .logo { font-size: 1.15rem; }
}
</style>
