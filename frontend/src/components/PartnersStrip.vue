<script setup>
import { t } from '../i18n'
import { ref } from 'vue'
import { api } from '../api'

const partners = ref([])
api('/partners/').then((d) => (partners.value = d)).catch(() => {})
</script>

<template>
  <section v-if="partners.length" class="partners">
    <div class="wrap">
      <h2>{{ t('Our partners') }}</h2>
      <div class="logos">
        <component
          :is="p.link ? 'a' : 'span'"
          v-for="p in partners"
          :key="p.id"
          :href="p.link || undefined"
          :target="p.link ? '_blank' : undefined"
          rel="noopener"
          class="partner"
          :title="p.name"
        >
          <img :src="p.logo" :alt="p.name" loading="lazy" />
        </component>
      </div>
    </div>
  </section>
</template>

<style scoped>
.partners { padding: 40px 0; border-top: 1px solid var(--line); text-align: center; }
.partners h2 { margin-bottom: 24px; }
.logos { display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 24px 40px; }
.partner img { display: block; max-height: 56px; max-width: 150px; object-fit: contain; filter: grayscale(1); opacity: .75; transition: .2s; }
a.partner:hover img { filter: none; opacity: 1; }
@media (max-width: 600px) { .logos { gap: 18px 24px; } .partner img { max-height: 44px; max-width: 110px; } }
</style>
