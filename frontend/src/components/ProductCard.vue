<script setup>
import { t } from '../i18n'
import PriceTag from './PriceTag.vue'
defineProps({ product: Object })
</script>

<template>
  <RouterLink :to="`/product/${product.slug}`" class="card-p">
    <div class="pic">
      <img v-if="product.image" :src="product.image" :alt="product.name" loading="lazy" />
      <span v-if="product.is_collection" class="tag coll">{{ t('Collection') }}</span>
      <span v-if="product.discount_percent" class="tag">-{{ product.discount_percent }}%</span>
    </div>
    <div class="info">
      <small class="muted">{{ product.category_name }}</small>
      <h3>{{ product.name }}</h3>
      <div class="row">
        <PriceTag :product="product" />
        <span class="dots">
          <i v-for="c in product.colors" :key="c.id" :style="{ background: c.hex }" :title="c.name"></i>
        </span>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.card-p { display: block; }
.pic { position: relative; aspect-ratio: 1; background: var(--plate); border-radius: var(--radius); overflow: hidden; }
.pic img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s ease; }
.card-p:hover .pic img { transform: scale(1.03); }
.card-p:hover h3 { text-decoration: underline; text-decoration-color: var(--gold); text-decoration-thickness: 1.5px; text-underline-offset: 4px; }
.tag { position: absolute; top: 10px; left: 10px; background: var(--gold-light); color: var(--wine-deep); font-size: .8rem; font-weight: 600; padding: 2px 8px; border-radius: var(--radius); font-variant-numeric: tabular-nums; }
.tag.coll { background: var(--wine); color: var(--on-wine); left: auto; right: 10px; }
.info { padding-top: 12px; }
small { font-size: .85rem; }
h3 { font-size: 1.3rem; margin: 0 0 6px; }
.row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.dots { display: flex; gap: 5px; }
.dots i { width: 12px; height: 12px; border-radius: 50%; box-shadow: inset 0 0 0 1px rgba(43, 26, 33, .2); display: block; }
@media (max-width: 600px) {
  h3 { font-size: 1.1rem; }
  .tag { top: 6px; left: 6px; font-size: .72rem; }
  .row { flex-wrap: wrap; gap: 4px; }
}
@media (prefers-reduced-motion: reduce) { .pic img { transition: none; } }
</style>
