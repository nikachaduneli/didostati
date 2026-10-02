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
.card-p { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; display: block; transition: box-shadow .15s, transform .15s; }
.card-p:hover { box-shadow: 0 8px 24px rgba(0,0,0,.1); transform: translateY(-3px); }
.pic { position: relative; aspect-ratio: 1; background: var(--line); }
.pic img { width: 100%; height: 100%; object-fit: cover; }
.tag { position: absolute; top: 10px; left: 10px; background: var(--sale); color: #fff; font-size: .8rem; font-weight: 700; padding: 3px 9px; border-radius: 999px; }
.tag.coll { background: var(--ink); left: auto; right: 10px; }
.info { padding: 12px 14px 16px; }
h3 { font-size: 1.05rem; margin: 2px 0 8px; }
.row { display: flex; justify-content: space-between; align-items: center; }
.dots { display: flex; gap: 4px; }
.dots i { width: 14px; height: 14px; border-radius: 50%; border: 1px solid var(--line); display: block; }
@media (max-width: 600px) {
  .info { padding: 10px 10px 12px; }
  h3 { font-size: .95rem; }
  .tag { top: 6px; left: 6px; font-size: .72rem; }
  .row { flex-wrap: wrap; gap: 4px; }
}
</style>
