<script setup>
import { t } from '../i18n'
import { money } from '../config'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { useCart } from '../stores/cart'
import PriceTag from '../components/PriceTag.vue'

const route = useRoute()
const router = useRouter()
const cart = useCart()
const product = ref(null)
const missing = ref(false)
const color = ref(null)
const size = ref(null)
const quantity = ref(1)
const active = ref(0)
const added = ref(false)

api(`/products/${route.params.slug}/`)
  .then((p) => {
    product.value = p
    document.title = `${p.name} · Didostati`
    color.value = p.colors[0] || null
    size.value = p.sizes?.[0] || null
  })
  .catch(() => (missing.value = true))

// Pictures tagged with the chosen colour come first; untagged ones are shown for every colour.
const gallery = computed(() => {
  const imgs = product.value?.images || []
  const mine = imgs.filter((i) => !color.value || i.color === null || i.color === color.value.id)
  return mine.length ? mine : imgs
})
const shown = computed(() => gallery.value[active.value]?.image || product.value?.image)

// Price of the chosen size (sizes without their own price inherit the product's).
const shownPrice = computed(() => {
  const p = product.value
  return size.value ? { ...p, price: size.value.price, final_price: size.value.final_price } : p
})

watch(gallery, (g) => { if (active.value >= g.length) active.value = 0 })

function go(n) {
  const len = gallery.value.length
  if (len) active.value = (n + len) % len
}
let touchX = null
function touchStart(e) { touchX = e.touches[0].clientX }
function touchEnd(e) {
  if (touchX === null) return
  const dx = e.changedTouches[0].clientX - touchX
  touchX = null
  if (Math.abs(dx) > 40) go(active.value + (dx < 0 ? 1 : -1))
}

function pick(c) {
  color.value = c
  const first = gallery.value.findIndex((i) => i.color === c.id)
  active.value = first >= 0 ? first : 0
}
function add(go) {
  cart.add(product.value, color.value, quantity.value, size.value)
  if (go) router.push('/cart')
  else {
    added.value = true
    setTimeout(() => (added.value = false), 1800)
  }
}
</script>

<template>
  <p v-if="missing" class="card center">{{ t('This product could not be found.') }} <RouterLink to="/shop" class="link">{{ t('Back to shop') }}</RouterLink></p>
  <div v-else-if="product" class="product">
    <div>
      <div class="stage">
      <!-- Faint, heavily blurred copy of the picture: tints the area behind it with the picture's colours. -->
      <Transition name="glow"><img v-if="shown" :key="shown" :src="shown" class="glow" alt="" aria-hidden="true" /></Transition>
      <div class="main" tabindex="0" @keydown.left="go(active - 1)" @keydown.right="go(active + 1)" @touchstart.passive="touchStart" @touchend="touchEnd">
        <img v-if="shown" :src="shown" :alt="product.name" />
        <template v-if="gallery.length > 1">
          <button type="button" class="nav prev" :aria-label="t('Previous image')" @click="go(active - 1)">‹</button>
          <button type="button" class="nav next" :aria-label="t('Next image')" @click="go(active + 1)">›</button>
          <span class="count">{{ active + 1 }} / {{ gallery.length }}</span>
        </template>
      </div>
      </div>
      <div v-if="gallery.length > 1" class="thumbs">
        <img v-for="(g, i) in gallery" :key="g.id" :src="g.image" :class="{ on: i === active }" :alt="`${product.name} ${i + 1}`" @click="active = i" />
      </div>
    </div>
    <div>
      <RouterLink :to="`/category/${product.category}`" class="muted">{{ product.category_name }}</RouterLink>
      <h1>{{ product.name }}</h1>
      <p class="big"><PriceTag :product="shownPrice" /> <span v-if="product.discount_percent" class="off">-{{ product.discount_percent }}%</span></p>
      <div class="desc" v-html="product.description"/>

      <div v-if="product.items?.length" class="includes card">
        <strong>{{ t('This collection includes:') }}</strong>
        <RouterLink v-for="i in product.items" :key="i.product.id" :to="`/product/${i.product.slug}`" class="inc">
          <img v-if="i.product.image" :src="i.product.image" :alt="i.product.name" />
          <span>{{ i.quantity }} × {{ i.product.name }}</span>
        </RouterLink>
        <small v-if="product.items_total > product.final_price" class="muted">
          {{ t('Bought separately: {n}', { n: money(product.items_total) }) }}
        </small>
      </div>

      <div v-if="product.colors.length" class="field">
        <label>{{ t('Colour:') }} <span class="muted">{{ color?.name }}</span></label>
        <div class="swatches">
          <button v-for="c in product.colors" :key="c.id" type="button" :title="c.name" :class="{ on: color?.id === c.id }" :style="{ background: c.hex }" @click="pick(c)"></button>
        </div>
      </div>
      <div v-if="product.sizes?.length" class="field">
        <label>{{ t('Size:') }} <span class="muted">{{ size?.name }}</span></label>
        <div class="sizes">
          <button v-for="s in product.sizes" :key="s.id" type="button" :class="{ on: size?.id === s.id }" @click="size = s">{{ s.name }}</button>
        </div>
      </div>
      <div class="field qty">
        <label for="q">{{ t('Quantity') }}</label>
        <input id="q" v-model.number="quantity" type="number" min="1" max="99" />
      </div>
      <div class="actions">
        <button class="btn" @click="add(false)">{{ added ? t('✓ Added') : t('Add to cart') }}</button>
        <button class="btn ghost" @click="add(true)">{{ t('Buy now') }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
.stage { position: relative; isolation: isolate; }
.glow { position: absolute; inset: -6%; width: 112%; height: 112%; object-fit: cover; z-index: -1; pointer-events: none; filter: blur(480px) saturate(1.4); opacity: 1; }
.glow-enter-active, .glow-leave-active { transition: opacity .6s ease; }
.glow-enter-from, .glow-leave-to { opacity: 0; }
@media (prefers-reduced-motion: reduce) { .glow-enter-active, .glow-leave-active { transition: none; } }
.main { position: relative; outline: none; aspect-ratio: 1; background: var(--line); border-radius: var(--radius); overflow: hidden; }
.main img { width: 100%; height: 100%; object-fit: cover; }
.nav { position: absolute; top: 50%; transform: translateY(-50%); width: 40px; height: 40px; border: 0; border-radius: 50%; background: rgba(255,255,255,.85); font-size: 1.6rem; line-height: 1; cursor: pointer; }
.prev { left: 10px; } .next { right: 10px; }
.count { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,.55); color: #fff; font-size: .8rem; padding: 2px 10px; border-radius: 999px; }
.thumbs { display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap; }
.thumbs img { width: 70px; height: 70px; object-fit: cover; border-radius: 8px; cursor: pointer; border: 2px solid transparent; }
.thumbs img.on { border-color: var(--accent); }
.big { font-size: 1.6rem; }
.off { background: var(--sale); color: #fff; font-size: .85rem; padding: 2px 9px; border-radius: 999px; vertical-align: middle; }
.desc { white-space: pre-line; color: var(--muted); }
.swatches { display: flex; gap: 10px; }
.swatches button { width: 34px; height: 34px; border-radius: 50%; border: 2px solid var(--line); cursor: pointer; padding: 0; box-shadow: inset 0 0 0 3px var(--card); }
.swatches button.on { border-color: var(--accent); }
.sizes { display: flex; gap: 8px; flex-wrap: wrap; }
.sizes button { min-width: 44px; padding: 8px 14px; border: 2px solid var(--line); border-radius: 8px; background: var(--card); font: inherit; cursor: pointer; }
.sizes button.on { border-color: var(--accent); color: var(--accent); font-weight: 700; }
.qty { max-width: 110px; }
.actions { display: flex; gap: 12px; flex-wrap: wrap; }
.product > * { min-width: 0; }
@media (max-width: 800px) { .product { grid-template-columns: 1fr; gap: 20px; overflow-x: clip; } }
@media (max-width: 600px) {
  .big { font-size: 1.4rem; }
  .thumbs { flex-wrap: nowrap; overflow-x: auto; }
  .thumbs img { flex: none; width: 60px; height: 60px; }
  .swatches button { width: 40px; height: 40px; }
  .actions .btn { flex: 1 1 100%; text-align: center; }
}
.includes { display: flex; flex-direction: column; gap: 8px; margin: 16px 0; padding: 14px; }
.inc { display: flex; align-items: center; gap: 10px; }
.inc:hover span { color: var(--accent); }
.inc img { width: 44px; height: 44px; object-fit: cover; border-radius: 6px; flex: none; }
</style>
