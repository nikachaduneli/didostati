<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { t } from '../i18n'

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
          v-for="(s, n) in slides"
          :key="s.id"
          v-bind="s.link ? (s.link.startsWith('http') ? { href: s.link } : { to: s.link }) : {}"
          :tabindex="n === i ? undefined : -1"
          :aria-hidden="n === i ? undefined : 'true'"
          class="slide"
          :class="{ bare: !s.title && !s.subtitle }"
      >
        <img :src="s.image" :alt="s.title" />
        <div v-if="s.title || s.subtitle" class="caption">
          <h2 v-if="s.title">{{ s.title }}</h2>
          <p v-if="s.subtitle">{{ s.subtitle }}</p>
        </div>
      </component>
    </div>
    <div v-if="slides.length > 1" class="controls">
      <div class="dots">
        <button v-for="(s, n) in slides" :key="s.id" :class="{ on: n === i }" :aria-label="`Slide ${n + 1}`" :aria-current="n === i" @click="go(n)" />
      </div>
      <button class="nav" :aria-label="t('Previous')" @click="go(i - 1)">‹</button>
      <button class="nav" :aria-label="t('Next')" @click="go(i + 1)">›</button>
    </div>
  </section>
</template>

<style scoped>
.slider { position: relative; overflow: hidden; margin-bottom: 16px; background: var(--wine); color: var(--on-wine); border-radius: var(--radius); }
.track { display: flex; transition: transform .6s cubic-bezier(.6, 0, .2, 1); }
/* picture on the left, wine panel with the words on the right: text never sits on an unknown picture */
.slide { flex: 0 0 100%; display: grid; grid-template-columns: minmax(0, 1.7fr) minmax(0, 1fr); min-height: 440px; }
.slide.bare { grid-template-columns: 1fr; }
.slide img { width: 100%; height: 100%; object-fit: cover; display: block; }
.caption { display: flex; flex-direction: column; justify-content: center; padding: 48px 48px 96px; }
.caption h2 { font-size: clamp(2rem, 3.6vw, 3.25rem); font-stretch: 66%; color: var(--gold-light); margin-bottom: .35em; }
.caption p { font-size: 1.15rem; margin: 0; max-width: 28ch; color: rgba(248, 243, 241, .85); }
a.slide:hover h2 { text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 6px; }
.controls { position: absolute; right: 0; bottom: 0; width: calc(100% / 2.7); display: flex; align-items: center; gap: 10px; padding: 0 48px 36px; }
.nav { width: 40px; height: 40px; border: 1.5px solid rgba(248, 243, 241, .4); border-radius: 50%; background: none; color: var(--on-wine); font-size: 1.5rem; line-height: 1; cursor: pointer; padding: 0 0 3px; }
.nav:hover { border-color: var(--gold-light); color: var(--gold-light); }
.dots { display: flex; gap: 6px; flex: 1; }
.dots button { flex: 1; max-width: 48px; height: 20px; padding: 0; border: 0; background: linear-gradient(rgba(248, 243, 241, .35), rgba(248, 243, 241, .35)) center / 100% 2px no-repeat; cursor: pointer; }
.dots button.on { background-image: linear-gradient(var(--gold-light), var(--gold-light)); background-size: 100% 3px; }
.slider :focus-visible { outline-color: var(--gold-light); }
@media (max-width: 800px) {
  .slide { grid-template-columns: 1fr; grid-template-rows: auto 1fr; min-height: 0; }
  .slide img { aspect-ratio: 4/3; height: auto; }
  .caption { padding: 24px 20px 76px; }
  .caption h2 { font-size: 2rem; }
  .caption p { font-size: 1rem; }
  .controls { width: 100%; padding: 0 20px 20px; }
}
@media (prefers-reduced-motion: reduce) { .track { transition: none; } }
</style>
