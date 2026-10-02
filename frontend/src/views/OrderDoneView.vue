<script setup>
import { t } from '../i18n'
import { money } from '../config'
import { useAuth } from '../stores/auth'

const auth = useAuth()
let order = null
try {
  order = JSON.parse(sessionStorage.getItem('lastOrder'))
} catch {}
</script>

<template>
  <div class="card center done">
    <h1>{{ t('Thank you! 🎉') }}</h1>
    <template v-if="order">
      <p>{{ t('Order') }} <strong>#{{ order.id }}</strong> {{ t("has been placed. We'll contact you at") }} <strong>{{ order.email }}</strong>.</p>
      <p class="muted">{{ t('Total:') }} {{ money(order.total) }} · {{ t('Delivering to') }} {{ order.line1 }}, {{ order.city }}</p>
    </template>
    <p v-else>{{ t('Your order has been placed.') }}</p>
    <p v-if="!auth.loggedIn" class="muted"><RouterLink to="/register" class="link">{{ t('Create an account') }}</RouterLink> {{ t('to track future orders.') }}</p>
    <RouterLink to="/shop" class="btn">{{ t('Continue shopping') }}</RouterLink>
  </div>
</template>

<style scoped>
.done { max-width: 560px; margin: 30px auto; }
</style>
