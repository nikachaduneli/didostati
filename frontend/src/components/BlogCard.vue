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
.post { display: block; }
img { width: 100%; aspect-ratio: 3/2; object-fit: cover; border-radius: var(--radius); background: var(--plate); }
.body { padding-top: 14px; }
small { font-size: .85rem; }
h3 { font-size: 1.4rem; margin: 2px 0 6px; }
.post:hover h3 { text-decoration: underline; text-decoration-color: var(--gold); text-decoration-thickness: 1.5px; text-underline-offset: 4px; }
p { margin: 0; max-width: 60ch; }
</style>
