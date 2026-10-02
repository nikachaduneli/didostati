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
      <div class="social">
        <a href="#" aria-label="Facebook" title="Facebook">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M13.5 22v-8.2h2.8l.5-3.3h-3.3V8.4c0-.9.4-1.7 1.8-1.7h1.6V3.9c-.3 0-1.3-.2-2.4-.2-2.5 0-4.1 1.5-4.1 4.2v2.6H7.6v3.3h2.8V22h3.1z"/></svg>
        </a>
        <a href="#" aria-label="Instagram" title="Instagram">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>
        </a>
      </div>
      <span class="muted">© {{ new Date().getFullYear() }} Didostati</span>
    </div>
  </footer>
</template>

<style scoped>
footer { border-top: 1px solid var(--line); background: var(--card); padding: 28px 0; margin-top: 0; }
.wrap { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; justify-content: space-between; }
.logo { color: var(--accent); font-size: 1.2rem; }
nav { display: flex; gap: 18px; }
.social { display: flex; gap: 14px; }
.social a { color: var(--muted); display: inline-flex; }
.social a:hover { color: var(--accent); }
@media (max-width: 600px) {
  footer { padding: 22px 0; }
  .wrap { flex-direction: column; align-items: flex-start; gap: 14px; }
  nav { flex-wrap: wrap; gap: 8px 18px; }
}
</style>
