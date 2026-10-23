<script setup>
import { t } from '../i18n'
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import ProductCard from '../components/ProductCard.vue'

const route = useRoute()
const router = useRouter()
const categories = ref([])
const data = ref({ results: [], count: 0, next: null, previous: null })
const loading = ref(true)

const f = reactive({
  search: route.query.search || '',
  ordering: route.query.ordering || 'newest',
  min_price: route.query.min_price || '',
  max_price: route.query.max_price || '',
  on_sale: route.query.on_sale === '1',
})
const page = computed(() => Number(route.query.page) || 1)
const slug = computed(() => route.params.slug || route.query.category || '')
const current = computed(() => categories.value.find((c) => c.slug === slug.value))
const pages = computed(() => Math.ceil(data.value.count / 12))

api('/categories/').then((d) => (categories.value = d))

async function load() {
  loading.value = true
  try {
    data.value = await api('/products/', {
      params: { ...f, on_sale: f.on_sale ? 1 : '', ordering: f.ordering, category: slug.value, page: page.value },
    })
  } finally {
    loading.value = false
  }
}
load()

function apply(p = 1) {
  router.push({
    path: route.path,
    query: { ...f, on_sale: f.on_sale ? 1 : '', ordering: f.ordering === 'newest' ? '' : f.ordering,
             category: route.params.slug ? '' : slug.value, page: p > 1 ? p : '' },
  })
}
watch(() => route.fullPath, load)
watch(current, (c) => c && (document.title = `${c.name} · Didostati`))
</script>

<template>
  <h1>{{ current ? current.name : f.search ? t('Results for “{q}”', { q: f.search }) : t('All products') }}</h1>
  <div v-if="current?.description" class="muted rich" v-html="current.description"></div>

  <div class="layout">
    <aside class="card">
      <form @submit.prevent="apply()">
        <div class="field">
          <label for="s">{{ t('Search') }}</label>
          <input id="s" v-model="f.search" type="search" :placeholder="t('Name, colour, category…')" />
        </div>
        <div class="field">
          <label>{{ t('Category') }}</label>
          <div class="cats">
            <RouterLink to="/shop" :class="{ on: !slug }">{{ t('All') }}</RouterLink>
            <RouterLink v-for="c in categories" :key="c.id" :to="`/category/${c.slug}`" :class="{ on: slug === c.slug }">{{ c.name }}</RouterLink>
          </div>
        </div>
        <div class="field grid2">
          <div><label for="mn">{{ t('Min price') }}</label><input id="mn" v-model="f.min_price" type="number" min="0" /></div>
          <div><label for="mx">{{ t('Max price') }}</label><input id="mx" v-model="f.max_price" type="number" min="0" /></div>
        </div>
        <div class="field">
          <label for="o">{{ t('Sort by') }}</label>
          <select id="o" v-model="f.ordering">
            <option value="newest">{{ t('Newest') }}</option>
            <option value="price_asc">{{ t('Price: low to high') }}</option>
            <option value="price_desc">{{ t('Price: high to low') }}</option>
            <option value="name">{{ t('Name') }}</option>
          </select>
        </div>
        <div class="field"><label class="check"><input v-model="f.on_sale" type="checkbox" /> {{ t('On sale only') }}</label></div>
        <button class="btn" style="width: 100%">{{ t('Apply') }}</button>
      </form>
    </aside>

    <section>
      <p class="muted">{{ t('{n} products', { n: data.count }) }}</p>
      <div v-if="data.results.length" class="grid" :style="{ opacity: loading ? 0.5 : 1 }">
        <ProductCard v-for="p in data.results" :key="p.id" :product="p" />
      </div>
      <p v-else-if="!loading" class="card center">{{ t('Nothing found. Try different words or filters.') }}</p>

      <div v-if="pages > 1" class="pager">
        <button class="btn ghost small" :disabled="page <= 1" @click="apply(page - 1)">{{ t('← Previous') }}</button>
        <span class="muted">{{ t('Page {p} of {n}', { p: page, n: pages }) }}</span>
        <button class="btn ghost small" :disabled="page >= pages" @click="apply(page + 1)">{{ t('Next →') }}</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.layout { display: grid; grid-template-columns: 250px 1fr; gap: 40px; align-items: start; margin-top: 18px; }
aside { position: sticky; top: 96px; }
.cats { display: flex; flex-direction: column; gap: 2px; }
.cats a { padding: 5px 10px; border-left: 2px solid transparent; color: var(--muted); }
.cats a:hover { color: var(--ink); }
.cats a.on { border-color: var(--gold); color: var(--wine); font-weight: 600; }
.pager { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 30px; }
@media (max-width: 800px) { .layout { grid-template-columns: 1fr; gap: 18px; } aside { position: static; } }
@media (max-width: 600px) {
  .cats { flex-direction: row; flex-wrap: nowrap; overflow-x: auto; gap: 6px; padding-bottom: 4px; -webkit-overflow-scrolling: touch; }
  .cats a { white-space: nowrap; border: 1px solid var(--field-line); border-radius: var(--radius); padding: 6px 14px; }
  .cats a.on { background: var(--wine); border-color: var(--wine); color: var(--on-wine); }
  .pager { gap: 8px; }
  .pager .muted { font-size: .85rem; text-align: center; }
}
</style>
