<script setup>
import { t } from '../i18n'
</script>

<template>
  <footer>
    <div class="wrap">
      <strong class="logo">Didostati</strong>
      <nav>
        <RouterLink to="/shop">{{ t('Shop') }}</RouterLink>
        <RouterLink to="/blog">{{ t('Blog') }}</RouterLink>
        <RouterLink to="/about">{{ t('About us') }}</RouterLink>
        <RouterLink to="/contact">{{ t('Contact') }}</RouterLink>
      </nav>
      <span class="muted">© {{ new Date().getFullYear() }} Didostati</span>
    </div>
  </footer>
</template>

<style scoped>
footer { border-top: 1px solid var(--line); background: var(--card); padding: 28px 0; margin-top: 0; }
.wrap { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; justify-content: space-between; }
.logo { color: var(--accent); font-size: 1.2rem; }
nav { display: flex; gap: 18px; }
@media (max-width: 600px) {
  footer { padding: 22px 0; }
  .wrap { flex-direction: column; align-items: flex-start; gap: 14px; }
  nav { flex-wrap: wrap; gap: 8px 18px; }
}
</style>
