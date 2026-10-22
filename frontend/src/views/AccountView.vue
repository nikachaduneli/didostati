<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, ApiError } from '../api'
import { money } from '../config'
import { t, fdate } from '../i18n'
import { useAuth } from '../stores/auth'

const auth = useAuth()
const router = useRouter()
const tab = ref('orders')
const orders = ref(null)
const addresses = ref([])
const blank = () => ({ id: null, label: '', full_name: '', phone: '', line1: '', line2: '', city: '', postal_code: '', country: '', is_default: false })
const form = reactive(blank())
const editing = ref(false)
const error = ref('')

api('/orders/').then((d) => (orders.value = d))
const loadAddresses = () => api('/addresses/').then((d) => (addresses.value = d))
loadAddresses()

function edit(a) {
  Object.assign(form, a ? { ...a } : blank())
  error.value = ''
  editing.value = true
}
async function save() {
  error.value = ''
  try {
    if (form.id) await api(`/addresses/${form.id}/`, { method: 'PUT', body: form })
    else await api('/addresses/', { method: 'POST', body: form })
    editing.value = false
    loadAddresses()
  } catch (e) {
    error.value = e instanceof ApiError ? e.text : t('Could not save.')
  }
}
async function del(a) {
  if (!confirm(t('Delete this address?'))) return
  await api(`/addresses/${a.id}/`, { method: 'DELETE' })
  loadAddresses()
}
async function makeDefault(a) {
  await api(`/addresses/${a.id}/`, { method: 'PATCH', body: { is_default: true } })
  loadAddresses()
}
async function logout() {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <div class="head">
    <div><h1>{{ t('My account') }}</h1><p class="muted">{{ auth.user.email }}</p></div>
    <button class="btn ghost small" @click="logout">{{ t('Sign out') }}</button>
  </div>
  <div class="tabs">
    <button :class="{ on: tab === 'orders' }" @click="tab = 'orders'">{{ t('Order history') }}</button>
    <button :class="{ on: tab === 'addresses' }" @click="tab = 'addresses'">{{ t('Saved addresses') }}</button>
  </div>

  <section v-if="tab === 'orders'">
    <p v-if="orders && !orders.length" class="card center">{{ t('No orders yet.') }} <RouterLink to="/shop" class="link">{{ t('Start shopping') }}</RouterLink></p>
    <div v-for="o in orders" :key="o.id" class="card order">
      <div class="oh">
        <strong>{{ t('Order') }} #{{ o.id }}</strong>
        <span class="muted">{{ fdate(o.created_at) }}</span>
        <span class="status">{{ t(o.status) }}</span>
        <span v-if="o.payment_status === 'pending'" class="muted">{{ t('Awaiting payment') }}</span>
        <span v-else-if="o.payment_status === 'failed'" class="muted">{{ t('Payment failed') }}</span>
        <strong class="total">{{ money(o.total) }}</strong>
      </div>
      <div v-for="(i, n) in o.items" :key="n" class="item">
        {{ i.quantity }} × {{ i.product_name }}<span v-if="i.color_name" class="muted"> ({{ i.color_name }})</span><span v-if="i.size_name" class="muted"> ({{ i.size_name }})</span>
        <span>{{ money(i.line_total) }}</span>
      </div>
      <small class="muted">{{ t('Shipped to') }} {{ o.full_name }}, {{ o.line1 }}, {{ o.city }}</small>
    </div>
  </section>

  <section v-else>
    <form v-if="editing" class="card" @submit.prevent="save">
      <h2>{{ form.id ? t('Edit address') : t('New address') }}</h2>
      <div v-if="error" class="error">{{ error }}</div>
      <div class="field"><label>{{ t('Label (e.g. Home)') }}</label><input v-model="form.label" /></div>
      <div class="grid2">
        <div class="field"><label>{{ t('Full name') }}</label><input v-model="form.full_name" required /></div>
        <div class="field"><label>{{ t('Phone') }}</label><input v-model="form.phone" required /></div>
      </div>
      <div class="field"><label>{{ t('Address') }}</label><input v-model="form.line1" required /></div>
      <div class="field"><label>{{ t('Apartment, floor… (optional)') }}</label><input v-model="form.line2" /></div>
      <div class="grid2">
        <div class="field"><label>{{ t('City') }}</label><input v-model="form.city" required /></div>
        <div class="field"><label>{{ t('Postal code') }}</label><input v-model="form.postal_code" /></div>
      </div>
      <div class="field"><label>{{ t('Country') }}</label><input v-model="form.country" required /></div>
      <div class="field"><label class="check"><input v-model="form.is_default" type="checkbox" /> {{ t('Default address') }}</label></div>
      <button class="btn">{{ t('Save') }}</button>
      <button type="button" class="btn ghost" style="margin-left: 8px" @click="editing = false">{{ t('Cancel') }}</button>
    </form>
    <template v-else>
      <button class="btn small" @click="edit()">{{ t('+ Add address') }}</button>
      <p v-if="!addresses.length" class="muted">{{ t('You have no saved addresses.') }}</p>
      <div class="addrs">
        <div v-for="a in addresses" :key="a.id" class="card">
          <strong>{{ a.label || t('Address') }}</strong> <span v-if="a.is_default" class="status">{{ t('default') }}</span>
          <div>{{ a.full_name }} · {{ a.phone }}</div>
          <div>{{ a.line1 }}<span v-if="a.line2">, {{ a.line2 }}</span></div>
          <div>{{ a.postal_code }} {{ a.city }}, {{ a.country }}</div>
          <p>
            <button class="link" @click="edit(a)">{{ t('Edit') }}</button> ·
            <button class="link" @click="del(a)">{{ t('Delete') }}</button>
            <template v-if="!a.is_default"> · <button class="link" @click="makeDefault(a)">{{ t('Make default') }}</button></template>
          </p>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: start; }
.tabs { display: flex; gap: 6px; border-bottom: 1px solid var(--line); margin-bottom: 22px; }
.tabs button { background: none; border: 0; border-bottom: 3px solid transparent; padding: 10px 14px; font: inherit; font-weight: 600; color: var(--muted); cursor: pointer; }
.tabs button.on { color: var(--wine); border-color: var(--gold); }
.order { margin-bottom: 16px; }
.oh { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 8px; }
.total { margin-left: auto; }
.item { display: flex; justify-content: space-between; padding: 3px 0; }
.status { background: var(--bg); border: 1px solid var(--line); border-radius: var(--radius); padding: 1px 10px; font-size: .8rem; text-transform: capitalize; }
.addrs { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-top: 16px; }
@media (max-width: 600px) {
  .head { gap: 12px; }
  .head > div { min-width: 0; overflow-wrap: anywhere; }
  .tabs { overflow-x: auto; white-space: nowrap; gap: 0; }
  .tabs button { padding: 10px 12px; flex: none; }
  .total { margin-left: 0; }
  .item { gap: 12px; }
  .addrs { grid-template-columns: 1fr; }
}
</style>
