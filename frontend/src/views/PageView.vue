<script setup>
import { t } from '../i18n'
import { reactive, ref } from 'vue'
import { api, ApiError } from '../api'

const props = defineProps({ slug: String, form: Boolean })
const page = ref(null)
const missing = ref(false)
const msg = reactive({ name: '', email: '', message: '' })
const sent = ref(false)
const error = ref('')

api(`/pages/${props.slug}/`).then((p) => (page.value = p)).catch(() => (missing.value = true))

async function send() {
  error.value = ''
  try {
    await api('/contact/', { method: 'POST', body: msg })
    sent.value = true
    Object.assign(msg, { name: '', email: '', message: '' })
  } catch (e) {
    error.value = e instanceof ApiError ? e.text : t('Could not send your message.')
  }
}
</script>

<template>
  <p v-if="missing" class="card center">{{ t('This page has not been written yet.') }}</p>
  <div v-else-if="page" class="narrow">
    <h1>{{ page.title }}</h1>
    <div class="rich" v-html="page.content"></div>

    <form v-if="form" class="card" style="margin-top: 32px" @submit.prevent="send">
      <h2>{{ t('Send us a message') }}</h2>
      <div v-if="sent" class="ok">{{ t("Thanks! We'll get back to you soon.") }}</div>
      <div v-if="error" class="error">{{ error }}</div>
      <div class="grid2">
        <div class="field"><label for="n">{{ t('Name') }}</label><input id="n" v-model="msg.name" required /></div>
        <div class="field"><label for="e">{{ t('Email') }}</label><input id="e" v-model="msg.email" type="email" required /></div>
      </div>
      <div class="field"><label for="m">{{ t('Message') }}</label><textarea id="m" v-model="msg.message" rows="5" required></textarea></div>
      <button class="btn">{{ t('Send') }}</button>
    </form>
  </div>
</template>

<style scoped>
.narrow { max-width: 820px; margin: 0 auto; }
</style>
