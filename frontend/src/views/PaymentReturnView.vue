<script setup>
import { t } from '../i18n'
import { onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { useCart } from '../stores/cart'

// The bank sends the customer back here. The real result is always read from our server, which asks the bank.
const route = useRoute()
const router = useRouter()
const cart = useCart()
const state = ref('checking') // checking | failed | missing
let tries = 0
let timer

async function check() {
  try {
    const order = await api(`/orders/status/${encodeURIComponent(route.query.order || '')}/`)
    if (order.payment_status === 'paid') {
      sessionStorage.setItem('lastOrder', JSON.stringify(order))
      cart.clear()
      router.replace('/order/done')
    } else if (order.payment_status === 'failed') {
      state.value = 'failed'
    } else if (++tries < 15) {
      timer = setTimeout(check, 2000) // the bank may need a few seconds to confirm
    } else {
      state.value = 'failed'
    }
  } catch {
    state.value = 'missing'
  }
}
check()
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <div class="card center box">
    <template v-if="state === 'checking'">
      <h1>{{ t('Confirming your payment…') }}</h1>
      <p class="muted">{{ t('Please do not close this page.') }}</p>
    </template>
    <template v-else-if="state === 'failed'">
      <h1>{{ t('Payment was not completed') }}</h1>
      <p class="muted">{{ t('You have not been charged. Your cart is still here, so you can try again.') }}</p>
      <RouterLink to="/checkout" class="btn">{{ t('Try again') }}</RouterLink>
    </template>
    <template v-else>
      <h1>{{ t('Order not found') }}</h1>
      <RouterLink to="/shop" class="btn">{{ t('Continue shopping') }}</RouterLink>
    </template>
  </div>
</template>

<style scoped>
.box { max-width: 560px; margin: 30px auto; }
</style>
