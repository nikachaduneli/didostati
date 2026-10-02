<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '../stores/cart'
import { useAuth } from '../stores/auth'
import { lang, setLang, t } from '../i18n'

const cart = useCart()
const auth = useAuth()
const router = useRouter()
const q = ref('')
const open = ref(false)

function search() {
  router.push({ path: '/shop', query: q.value.trim() ? { search: q.value.trim() } : {} })
  open.value = false
}
</script>

<template>
  <header class="top">
    <div class="wrap bar">
      <RouterLink to="/" class="logo">Didostati</RouterLink>
      <button class="burger" :aria-label="t('Menu')" @click="open = !open">☰</button>
      <nav :class="{ open }" @click="open = false">
        <RouterLink to="/">{{ t('Home') }}</RouterLink>
        <RouterLink to="/shop">{{ t('Shop') }}</RouterLink>
        <RouterLink to="/blog">{{ t('Blog') }}</RouterLink>
        <RouterLink to="/about">{{ t('About us') }}</RouterLink>
        <RouterLink to="/contact">{{ t('Contact') }}</RouterLink>
      </nav>
      <form class="search" @submit.prevent="search">
        <input v-model="q" type="search" :placeholder="t('Search products…')" :aria-label="t('Search products')" />
      </form>
      <div class="langs">
        <button v-for="c in ['en', 'ka']" :key="c" :class="{ on: lang === c }" @click="setLang(c)">{{ c.toUpperCase() }}</button>
      </div>
      <div class="actions">
        <RouterLink v-if="auth.loggedIn" to="/account">{{ auth.user.first_name || t('Account') }}</RouterLink>
        <RouterLink v-else to="/login">{{ t('Sign in') }}</RouterLink>
        <RouterLink to="/cart" class="cart">{{ t('Cart') }} <span v-if="cart.count" class="badge">{{ cart.count }}</span></RouterLink>
      </div>
    </div>
  </header>
</template>

<style scoped>
.top { position: sticky; top: 0; z-index: 10; background: var(--card); border-bottom: 1px solid var(--line); }
.bar { display: flex; align-items: center; gap: 22px; min-height: 64px; flex-wrap: wrap; }
.logo { font-size: 1.5rem; font-weight: 800; letter-spacing: -.02em; color: var(--accent); }
nav { display: flex; gap: 18px; }
nav a { color: var(--muted); font-weight: 500; }
nav a:hover, nav a.router-link-exact-active { color: var(--ink); }
.search { flex: 1; max-width: 320px; margin-left: auto; }
.search input { border-radius: 999px; padding: 8px 16px; }
.langs { display: flex; gap: 2px; border: 1px solid var(--line); border-radius: 999px; padding: 2px; }
.langs button { border: 0; background: none; color: var(--muted); font: inherit; font-size: .8rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; cursor: pointer; }
.langs button.on { background: var(--accent); color: #fff; }
.actions { display: flex; gap: 18px; align-items: center; font-weight: 500; }
.badge { background: var(--accent); color: #fff; border-radius: 999px; font-size: .75rem; padding: 2px 7px; margin-left: 2px; }
.burger { display: none; background: none; border: 0; font-size: 1.5rem; color: inherit; margin-left: auto; cursor: pointer; }
@media (max-width: 820px) {
  .bar { gap: 10px 12px; min-height: 56px; padding-top: 8px; padding-bottom: 8px; }
  .logo { font-size: 1.3rem; order: 1; }
  .actions { order: 2; margin-left: auto; gap: 14px; white-space: nowrap; }
  .burger { display: block; order: 3; margin-left: 0; padding: 4px 8px; min-width: 44px; min-height: 44px; }
  .search { order: 4; flex: 1 1 0; min-width: 0; max-width: none; margin: 0; }
  .langs { order: 5; }
  nav { display: none; order: 6; width: 100%; flex-direction: column; gap: 0; padding-bottom: 6px; }
  nav a { padding: 11px 4px; border-top: 1px solid var(--line); }
  nav.open { display: flex; }
}
@media (max-width: 380px) {
  .actions { gap: 10px; font-size: .9rem; }
  .logo { font-size: 1.15rem; }
}
</style>
