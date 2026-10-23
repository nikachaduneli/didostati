<script setup>
import { ref, onMounted } from 'vue'
import { lang, t } from '../i18n'
import { api } from '../api'
import mark from '../assets/logo-mark.png'

const social = ref({ facebook: '', instagram: '' })
onMounted(async () => {
  try { social.value = await api('/social/') } catch { /* links stay hidden */ }
})
</script>

<template>
  <footer>
    <div class="wrap">
      <RouterLink to="/" class="logo" :style="{ '--mark': `url(${mark})` }">
        <span class="mark" aria-hidden="true"></span>{{ lang === 'ka' ? 'დიდოსტატი' : 'Didostati' }}
      </RouterLink>
      <nav>
        <RouterLink to="/shop">{{ t('Shop') }}</RouterLink>
        <RouterLink to="/blog">{{ t('Blog') }}</RouterLink>
        <RouterLink to="/about">{{ t('About us') }}</RouterLink>
        <RouterLink to="/contact">{{ t('Contact') }}</RouterLink>
      </nav>
      <div class="social">
        <a v-if="social.facebook" :href="social.facebook" target="_blank" rel="noopener" aria-label="Facebook" title="Facebook">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M13.5 22v-8.2h2.8l.5-3.3h-3.3V8.4c0-.9.4-1.7 1.8-1.7h1.6V3.9c-.3 0-1.3-.2-2.4-.2-2.5 0-4.1 1.5-4.1 4.2v2.6H7.6v3.3h2.8V22h3.1z"/></svg>
        </a>
        <a v-if="social.instagram" :href="social.instagram" target="_blank" rel="noopener" aria-label="Instagram" title="Instagram">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>
        </a>
      </div>
      <span class="copy">© {{ new Date().getFullYear() }} Didostati</span>
    </div>
  </footer>
</template>

<style scoped>
footer { background: var(--wine); color: var(--on-wine); padding: 40px 0 32px; }
footer::before { content: ''; display: block; height: 2px; background: var(--hem); margin-top: -40px; margin-bottom: 40px; }
.wrap { display: flex; gap: 28px; align-items: center; flex-wrap: wrap; justify-content: space-between; }
.logo { display: inline-flex; align-items: center; gap: 10px; font-family: var(--logo); font-size: 1.6rem; font-weight: 400; line-height: 1; color: var(--gold-light); }
.mark { width: 36px; height: 36px; background: var(--gold-light); -webkit-mask: var(--mark) center / contain no-repeat; mask: var(--mark) center / contain no-repeat; }
nav { display: flex; gap: 22px; }
nav a { color: rgba(248, 243, 241, .8); }
nav a:hover { color: var(--gold-light); }
.social { display: flex; gap: 16px; }
.social a { color: rgba(248, 243, 241, .8); display: inline-flex; }
.social a:hover { color: var(--gold-light); }
.copy { color: rgba(248, 243, 241, .65); font-size: .9rem; }
footer :focus-visible { outline-color: var(--gold-light); }
@media (max-width: 600px) {
  .wrap { flex-direction: column; align-items: flex-start; gap: 18px; }
  nav { flex-wrap: wrap; gap: 8px 20px; }
}
</style>
