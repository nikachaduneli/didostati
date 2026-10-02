<script setup>
import { t } from '../i18n'
import { ref } from 'vue'
import { api } from '../api'
import BlogCard from './BlogCard.vue'

const posts = ref([])
api('/blogs/', { params: { limit: 3 } }).then((d) => (posts.value = d)).catch(() => {})
</script>

<template>
  <section v-if="posts.length" class="strip">
    <div class="wrap">
      <div class="section-head">
        <h2>{{ t('From our blog') }}</h2>
        <RouterLink to="/blog" class="link">{{ t('All posts →') }}</RouterLink>
      </div>
      <div class="grid">
        <BlogCard v-for="p in posts" :key="p.id" :post="p" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.strip { padding: 48px 0; border-top: 1px solid var(--line); }
</style>
