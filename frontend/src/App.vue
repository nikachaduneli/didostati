<script setup>
import SiteHeader from './components/SiteHeader.vue'
import SiteFooter from './components/SiteFooter.vue'
import BlogStrip from './components/BlogStrip.vue'
import { watch } from 'vue'
import { useCart } from './stores/cart'
import { lang } from './i18n'

const cart = useCart()
cart.refresh()
watch(lang, () => cart.refresh())
</script>

<template>
  <SiteHeader />
  <main class="wrap page">
    <RouterView :key="$route.fullPath + lang" />
  </main>
  <BlogStrip :key="lang" />
  <SiteFooter />
</template>
