<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'

const slides = ref([])
const i = ref(0)
let timer

function go(n) {
  if (!slides.value.length) return
  i.value = (n + slides.value.length) % slides.value.length
  start()
}
function start() {
  clearInterval(timer)
  if (slides.value.length > 1) timer = setInterval(() => (i.value = (i.value + 1) % slides.value.length), 5000)
}

onMounted(async () => {
  slides.value = await api('/slides/').catch(() => [])
  start()
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <section v-if="slides.length" class="slider" @mouseenter="clearInterval(timer)" @mouseleave="start">
    <div class="track" :style="{ transform: `translateX(-${i * 100}%)` }">
      <component
          :is="s.link ? (s.link.startsWith('http') ? 'a' : 'RouterLink') : 'div'"
          v-for="s in slides"
          :key="s.id"
          v-bind="s.link ? (s.link.startsWith('http') ? { href: s.link } : { to: s.link }) : {}"
          class="slide"
      >
        <img :src="s.image" :alt="s.title" />
        <div v-if="s.title || s.subtitle" class="caption">
          <h2 v-if="s.title">{{ s.title }}</h2>
          <p v-if="s.subtitle">{{ s.subtitle }}</p>
        </div>
      </component>
    </div>
    <template v-if="slides.length > 1">
      <button class="nav prev" aria-label="Previous" @click="go(i - 1)">‹</button>
      <button class="nav next" aria-label="Next" @click="go(i + 1)">›</button>
      <div class="dots">
        <button v-for="(s, n) in slides" :key="s.id" :class="{ on: n === i }" :aria-label="`Slide ${n + 1}`" @click="go(n)" />
      </div>
    </template>
  </section>
</template>

<style scoped>
.slider { position: relative; overflow: hidden; border-radius: var(--radius); margin-bottom: 32px; background: var(--line); }
.track { display: flex; transition: transform .5s ease; }
.slide { position: relative; flex: 0 0 100%; display: block; aspect-ratio: 21/8; }
.slide img { width: 100%; height: 100%; object-fit: cover; display: block; }
.caption { position: absolute; inset: auto 0 0 0; padding: 60px 48px 36px; color: #fff; background: linear-gradient(transparent, rgba(0,0,0,.65)); }
.caption h2 { font-size: clamp(1.4rem, 3.5vw, 2.6rem); letter-spacing: -.02em; }
.caption p { font-size: clamp(.95rem, 1.6vw, 1.2rem); margin-top: 4px; }
.nav { position: absolute; top: 50%; transform: translateY(-50%); width: 44px; height: 44px; border: 0; border-radius: 50%; background: rgba(255,255,255,.85); font-size: 1.8rem; line-height: 1; cursor: pointer; }
.prev { left: 14px; } .next { right: 14px; }
.dots { position: absolute; bottom: 12px; left: 0; right: 0; display: flex; justify-content: center; gap: 8px; }
.dots button { width: 10px; height: 10px; padding: 0; border: 0; border-radius: 50%; background: rgba(255,255,255,.55); cursor: pointer; }
.dots button.on { background: #fff; }
@media (max-width: 600px) {
  .slide { aspect-ratio: 16/9; }
  .caption { padding: 30px 16px 28px; }
  .nav { width: 34px; height: 34px; font-size: 1.4rem; }
}
</style>
