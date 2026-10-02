<script setup>
import { money } from '../config'
defineProps({ product: Object })
</script>

<template>
  <span class="price">
    <s v-if="product.discount_percent">{{ money(product.price) }}</s>
    <span class="now" :class="{ sale: product.discount_percent }">{{ money(product.final_price) }}</span>
  </span>
</template>
