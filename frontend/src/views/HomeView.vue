<script setup>
import { t } from '../i18n'
import { ref } from 'vue'
import { api } from '../api'
import ProductCard from '../components/ProductCard.vue'
import HeroSlider from '../components/HeroSlider.vue'

const categories = ref([])
const popular = ref([])
api('/categories/').then((d) => (categories.value = d))
api('/products/', { params: { popular: 1 } }).then((d) => (popular.value = d))
</script>

<template>
  <HeroSlider />

  <section class="section">
    <div class="section-head"><h2>{{ t('Shop by category') }}</h2></div>
    <div class="cats">
      <RouterLink
          v-for="c in [...categories].sort((a, b) => a.order - b.order)"
          :key="c.id"
          :to="`/category/${c.slug}`"
          class="cat"
      >
        <div class="arch"><img :src="c.image" alt="" loading="lazy" /></div>
        <strong>{{ c.name }}</strong>
        <small class="muted">{{ t('{n} products', { n: c.product_count }) }}</small>
      </RouterLink>
    </div>
  </section>

  <section v-if="popular.length" class="section">
    <div class="section-head">
      <h2>{{ t('Popular products') }}</h2>
      <RouterLink to="/shop" class="link">{{ t('See all') }}</RouterLink>
    </div>
    <div class="grid">
      <ProductCard v-for="p in popular" :key="p.id" :product="p" />
    </div>
  </section>
</template>

<style scoped>
.cats { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 32px 24px; }
.cat { display: flex; flex-direction: column; align-items: center; text-align: center; }
/* arched like the windows of a Georgian church */
.arch { width: 100%; aspect-ratio: 4/5; border-radius: 999px 999px var(--radius) var(--radius); overflow: hidden; background: var(--plate); margin-bottom: 16px; outline: 1.5px solid transparent; outline-offset: 6px; transition: outline-color .2s; }
.arch img { width: 100%; height: 100%; object-fit: cover; }
.cat:hover .arch { outline-color: var(--gold); }
.cat strong { font-family: var(--display); font-stretch: 72%; font-weight: 650; font-size: 1.5rem; line-height: 1.2; }
.cat:focus-visible { outline: 0; }
.cat:focus-visible .arch { outline: 2px solid var(--gold); }
@media (max-width: 600px) {
  .cats { grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 24px 12px; }
  .arch { margin-bottom: 10px; outline-offset: 4px; }
  .cat strong { font-size: 1.1rem; }
  .cat small { font-size: .8rem; }
}
</style>
