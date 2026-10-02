<script setup>
import { t } from '../i18n'
import { ref } from 'vue'
import { api } from '../api'
import BlogCard from '../components/BlogCard.vue'

const posts = ref([])
api('/blogs/', { params: { limit: 100 } }).then((d) => (posts.value = d))
</script>

<template>
  <h1>{{ t('Blog') }}</h1>
  <div class="grid"><BlogCard v-for="p in posts" :key="p.id" :post="p" /></div>
  <p v-if="!posts.length" class="muted">{{ t('No posts yet.') }}</p>
</template>
