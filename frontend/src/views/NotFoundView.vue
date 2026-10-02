<script setup>
import { t } from '../i18n'
</script>

<template>
  <div class="card center">
    <h1>{{ t('Page not found') }}</h1>
    <RouterLink to="/" class="btn">{{ t('Go home') }}</RouterLink>
  </div>
</template>
