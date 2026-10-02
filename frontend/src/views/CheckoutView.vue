<script setup>
import { t } from '../i18n'
import { reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api, ApiError } from '../api'
import { money } from '../config'
import { useAuth } from '../stores/auth'
import { useCart } from '../stores/cart'

const auth = useAuth()
const cart = useCart()
const router = useRouter()

const empty = { full_name: '', phone: '', line1: '', line2: '', city: '', postal_code: '', country: '' }
const form = reactive({ email: auth.user?.email || '', ...empty, note: '' })
const addresses = ref([])
const chosen = ref('')
const saveAddress = ref(false)
const busy = ref(false)
const error = ref('')

if (auth.loggedIn) {
  api('/addresses/').then((list) => {
    addresses.value = list
    const def = list.find((a) => a.is_default) || list[0]
    if (def) chosen.value = def.id
  })
}
watch(chosen, (id) => {
  const a = addresses.value.find((x) => x.id === id)
  Object.assign(form, a ? Object.fromEntries(Object.keys(empty).map((k) => [k, a[k]])) : empty)
})

async function submit() {
  busy.value = true
  error.value = ''
  try {
    const order = await api('/orders/', { method: 'POST', body: { ...form, lines: cart.payload } })
    if (auth.loggedIn && saveAddress.value && !chosen.value) {
      await api('/addresses/', { method: 'POST', body: { label: 'Saved at checkout', ...Object.fromEntries(Object.keys(empty).map((k) => [k, form[k]])) } }).catch(() => {})
    }
    sessionStorage.setItem('lastOrder', JSON.stringify(order))
    cart.clear()
    router.push('/order/done')
  } catch (e) {
    error.value = e instanceof ApiError ? e.text : t('Something went wrong. Please try again.')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <h1>{{ t('Checkout') }}</h1>
  <div v-if="!cart.items.length" class="card center">
    <p>{{ t('Your cart is empty.') }}</p>
    <RouterLink to="/shop" class="btn">{{ t('Start shopping') }}</RouterLink>
  </div>
  <div v-else class="layout">
    <form class="card" @submit.prevent="submit">
      <p v-if="!auth.loggedIn" class="muted">
        {{ t('Checking out as a guest.') }} <RouterLink to="/login?next=/checkout" class="link">{{ t('Sign in') }}</RouterLink> {{ t('to use saved addresses and see your order history.') }}
      </p>
      <div v-if="error" class="error">{{ error }}</div>

      <div v-if="addresses.length" class="field">
        <label for="saved">{{ t('Saved address') }}</label>
        <select id="saved" v-model="chosen">
          <option v-for="a in addresses" :key="a.id" :value="a.id">{{ a.label || a.full_name }} — {{ a.line1 }}, {{ a.city }}</option>
          <option value="">{{ t('Use a new address…') }}</option>
        </select>
      </div>

      <div class="field"><label for="email">{{ t('Email') }}</label><input id="email" v-model="form.email" type="email" required autocomplete="email" /></div>
      <div class="grid2">
        <div class="field"><label for="name">{{ t('Full name') }}</label><input id="name" v-model="form.full_name" required autocomplete="name" /></div>
        <div class="field"><label for="phone">{{ t('Phone') }}</label><input id="phone" v-model="form.phone" required autocomplete="tel" /></div>
      </div>
      <div class="field"><label for="l1">{{ t('Address') }}</label><input id="l1" v-model="form.line1" required autocomplete="address-line1" /></div>
      <div class="field"><label for="l2">{{ t('Apartment, floor… (optional)') }}</label><input id="l2" v-model="form.line2" autocomplete="address-line2" /></div>
      <div class="grid2">
        <div class="field"><label for="city">{{ t('City') }}</label><input id="city" v-model="form.city" required autocomplete="address-level2" /></div>
        <div class="field"><label for="zip">{{ t('Postal code') }}</label><input id="zip" v-model="form.postal_code" autocomplete="postal-code" /></div>
      </div>
      <div class="field"><label for="country">{{ t('Country') }}</label><input id="country" v-model="form.country" required autocomplete="country-name" /></div>
      <div class="field"><label for="note">{{ t('Order note (optional)') }}</label><textarea id="note" v-model="form.note" rows="2"></textarea></div>
      <div v-if="auth.loggedIn && !chosen" class="field"><label class="check"><input v-model="saveAddress" type="checkbox" /> {{ t('Save this address to my account') }}</label></div>

      <button class="btn" :disabled="busy">{{ busy ? t('Placing order…') : t('Place order') }}</button>
      <p class="muted"><small>{{ t('Payment is collected on delivery.') }}</small></p>
    </form>

    <aside class="card">
      <h2>{{ t('Your order') }}</h2>
      <div v-for="i in cart.items" :key="i.product + '-' + i.color" class="row">
        <span>{{ i.quantity }} × {{ i.name }}<small v-if="i.colorName" class="muted"> ({{ i.colorName }})</small></span>
        <span>{{ money(i.unitPrice * i.quantity) }}</span>
      </div>
      <p class="row tot"><span>{{ t('Total') }}</span><strong>{{ money(cart.total) }}</strong></p>
    </aside>
  </div>
</template>

<style scoped>
.layout { display: grid; grid-template-columns: 1fr 340px; gap: 24px; align-items: start; }
.row { display: flex; justify-content: space-between; gap: 12px; padding: 6px 0; }
.tot { border-top: 1px solid var(--line); margin-top: 8px; padding-top: 12px; font-size: 1.15rem; }
@media (max-width: 800px) { .layout { grid-template-columns: 1fr; } }
.layout > * { min-width: 0; }
</style>
