<script setup>
import { t, fdate } from '../i18n'
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'

const post = ref(null)
const missing = ref(false)
api(`/blogs/${useRoute().params.slug}/`)
  .then((p) => {
    post.value = p
    document.title = `${p.title} · Didostati`
  })
  .catch(() => (missing.value = true))
</script>

<template>
  <p v-if="missing" class="card center">{{ t('Post not found.') }} <RouterLink to="/blog" class="link">{{ t('All posts') }}</RouterLink></p>
  <article v-else-if="post" class="post">
    <RouterLink to="/blog" class="muted">{{ t('← Blog') }}</RouterLink>
    <h1>{{ post.title }}</h1>
    <p class="muted">{{ fdate(post.created_at) }}</p>
    <img v-if="post.cover_image" :src="post.cover_image" :alt="post.title" class="cover" />
    <!-- content is authored by staff in the admin editor -->
    <div class="rich" v-html="post.content"></div>
  </article>
</template>

<style scoped>
.post { max-width: 780px; margin: 0 auto; }
.cover { width: 100%; max-height: 420px; object-fit: cover; border-radius: var(--radius); margin-bottom: 24px; }
</style>
