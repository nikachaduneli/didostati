<script setup>
import { fdate } from '../i18n'
defineProps({ post: Object })
</script>

<template>
  <RouterLink :to="`/blog/${post.slug}`" class="post">
    <img v-if="post.cover_image" :src="post.cover_image" :alt="post.title" loading="lazy" />
    <div class="body">
      <small class="muted">{{ fdate(post.created_at) }}</small>
      <h3>{{ post.title }}</h3>
      <p class="muted">{{ post.excerpt }}</p>
    </div>
  </RouterLink>
</template>

<style scoped>
.post { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; display: block; transition: transform .15s; }
.post:hover { transform: translateY(-3px); }
img { width: 100%; aspect-ratio: 16/10; object-fit: cover; }
.body { padding: 14px 16px 18px; }
h3 { font-size: 1.1rem; margin: 4px 0 6px; }
p { margin: 0; }
</style>
