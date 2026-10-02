<script setup>
import { t } from '../i18n'
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiError } from '../api'
import { useAuth } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuth()
const isRegister = computed(() => route.path === '/register')
const form = reactive({ email: '', password: '', first_name: '' })
const error = ref('')
const busy = ref(false)

async function submit() {
  busy.value = true
  error.value = ''
  try {
    if (isRegister.value) await auth.register({ ...form })
    else await auth.login(form.email, form.password)
    router.push(route.query.next || '/account')
  } catch (e) {
    error.value = e instanceof ApiError ? e.text : t('Something went wrong.')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <form class="card box" @submit.prevent="submit">
    <h1>{{ isRegister ? t('Create account') : t('Sign in') }}</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="isRegister" class="field"><label for="fn">{{ t('First name') }}</label><input id="fn" v-model="form.first_name" autocomplete="given-name" /></div>
    <div class="field"><label for="em">{{ t('Email') }}</label><input id="em" v-model="form.email" type="email" required autocomplete="email" /></div>
    <div class="field"><label for="pw">{{ t('Password') }}</label><input id="pw" v-model="form.password" type="password" required :autocomplete="isRegister ? 'new-password' : 'current-password'" /></div>
    <button class="btn" :disabled="busy" style="width: 100%">{{ isRegister ? t('Create account') : t('Sign in') }}</button>
    <p class="center muted">
      <template v-if="isRegister">{{ t('Already have an account?') }} <RouterLink :to="{ path: '/login', query: route.query }" class="link">{{ t('Sign in') }}</RouterLink></template>
      <template v-else>New here? <RouterLink :to="{ path: '/register', query: route.query }" class="link">{{ t('Create an account') }}</RouterLink></template>
    </p>
  </form>
</template>

<style scoped>
.box { max-width: 420px; margin: 20px auto; }
</style>
