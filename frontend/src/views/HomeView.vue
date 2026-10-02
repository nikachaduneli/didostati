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
        <img :src="c.image" :alt="c.name" loading="lazy" />
        <div class="label">
          <strong>{{ c.name }}</strong>
          <small>{{ t('{n} products', { n: c.product_count }) }}</small>
        </div>
      </RouterLink>
    </div>
  </section>

  <section v-if="popular.length" class="section">
    <div class="section-head">
      <h2>{{ t('Popular products') }}</h2>
      <RouterLink to="/shop" class="link">{{ t('See all →') }}</RouterLink>
    </div>
    <div class="grid">
      <ProductCard v-for="p in popular" :key="p.id" :product="p" />
    </div>
  </section>
</template>

<style scoped>
.hero { text-align: center; padding: 56px 16px; background: var(--card); border: 1px solid var(--line); border-radius: 20px; }
.hero h1 { font-size: clamp(2rem, 5vw, 3.2rem); letter-spacing: -.02em; }
.hero p { color: var(--muted); font-size: 1.15rem; margin-bottom: 24px; }
.cats { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 22px; }
.cat { position: relative; border-radius: var(--radius); overflow: hidden; aspect-ratio: 4/3; display: block; background: var(--line); }
.cat img { width: 100%; height: 100%; object-fit: cover; transition: transform .3s; }
.cat:hover img { transform: scale(1.05); }
.label { position: absolute; inset: auto 0 0 0; padding: 36px 18px 14px; color: #fff; display: flex; flex-direction: column; background: linear-gradient(transparent, rgba(0,0,0,.65)); }
.label strong { font-size: 1.25rem; }
@media (max-width: 600px) {
  .hero { padding: 36px 16px; border-radius: 14px; }
  .hero p { font-size: 1rem; }
  .cats { grid-template-columns: 1fr 1fr; gap: 12px; }
  .label { padding: 24px 12px 10px; }
  .label strong { font-size: 1rem; }
}
</style>
