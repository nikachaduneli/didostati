<script setup>
import { t } from '../i18n'
import { money } from '../config'
import { useCart } from '../stores/cart'

const cart = useCart()
cart.refresh()
</script>

<template>
  <h1>{{ t('Your cart') }}</h1>
  <div v-if="!cart.items.length" class="card center">
    <p>{{ t('Your cart is empty.') }}</p>
    <RouterLink to="/shop" class="btn">{{ t('Start shopping') }}</RouterLink>
  </div>
  <div v-else class="layout">
    <div class="card">
      <div v-for="i in cart.items" :key="i.product + '-' + i.color + '-' + i.size" class="line">
        <img :src="i.image" :alt="i.name" />
        <div class="name">
          <RouterLink :to="`/product/${i.slug}`"><strong>{{ i.name }}</strong></RouterLink>
          <div class="muted" v-if="i.colorName">{{ t('Colour:') }} {{ i.colorName }}</div>
          <div class="muted" v-if="i.sizeName">{{ t('Size:') }} {{ i.sizeName }}</div>
          <button class="link" @click="cart.remove(i)">{{ t('Remove') }}</button>
        </div>
        <input type="number" min="1" max="99" :value="i.quantity" :aria-label="t('Quantity')" @change="cart.setQuantity(i, +$event.target.value)" />
        <div class="sum">{{ money(i.unitPrice * i.quantity) }}</div>
      </div>
    </div>
    <aside class="card">
      <h2>{{ t('Summary') }}</h2>
      <p class="tot"><span>{{ t('Total') }}</span> <strong>{{ money(cart.total) }}</strong></p>
      <RouterLink to="/checkout" class="btn" style="width: 100%; text-align: center">{{ t('Checkout') }}</RouterLink>
      <p class="muted center"><small>{{ t('No account needed.') }}</small></p>
    </aside>
  </div>
</template>

<style scoped>
.layout { display: grid; grid-template-columns: 1fr 320px; gap: 24px; align-items: start; }
.line { display: grid; grid-template-columns: 80px 1fr 80px 90px; gap: 16px; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--line); }
.line:last-child { border-bottom: 0; }
.line img { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; }
.sum { text-align: right; font-weight: 700; }
.tot { display: flex; justify-content: space-between; font-size: 1.2rem; }
.name { min-width: 0; overflow-wrap: anywhere; }
@media (max-width: 800px) { .layout { grid-template-columns: 1fr; } }
@media (max-width: 600px) {
  .line { grid-template-columns: 64px 1fr 72px; gap: 10px 12px; align-items: start; }
  .line img { width: 64px; height: 64px; }
  .sum { grid-column: 2 / 4; text-align: left; }
}
</style>
