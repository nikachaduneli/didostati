import { defineStore } from 'pinia'
import { api } from '../api'

const KEY = 'cart'
const load = () => {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || []
  } catch {
    return []
  }
}

// The cart lives in the browser so guests can shop without an account.
// Each item: { product, color, quantity, name, slug, image, colorName, unitPrice }.
// Prices shown here are only a snapshot; the server re-prices at checkout.
export const useCart = defineStore('cart', {
  state: () => ({ items: load() }),
  getters: {
    count: (s) => s.items.reduce((n, i) => n + i.quantity, 0),
    total: (s) => s.items.reduce((n, i) => n + i.unitPrice * i.quantity, 0),
    payload: (s) => s.items.map((i) => ({ product: i.product, color: i.color, quantity: i.quantity })),
  },
  actions: {
    _save() {
      localStorage.setItem(KEY, JSON.stringify(this.items))
    },
    add(product, color, quantity = 1) {
      const colorId = color?.id ?? null
      const found = this.items.find((i) => i.product === product.id && i.color === colorId)
      if (found) found.quantity = Math.min(99, found.quantity + quantity)
      else
        this.items.push({
          product: product.id,
          color: colorId,
          colorName: color?.name ?? '',
          quantity,
          name: product.name,
          slug: product.slug,
          image: product.image,
          unitPrice: Number(product.final_price),
        })
      this._save()
    },
    setQuantity(item, q) {
      item.quantity = Math.max(1, Math.min(99, q || 1))
      this._save()
    },
    remove(item) {
      this.items = this.items.filter((i) => i !== item)
      this._save()
    },
    clear() {
      this.items = []
      this._save()
    },
    /** Re-price against the server; drops products that no longer exist. */
    async refresh() {
      if (!this.items.length) return
      try {
        const { lines } = await api('/cart/price/', { method: 'POST', body: { lines: this.payload } })
        this.items = lines.map((l) => {
          return {
            product: l.product.id,
            color: l.color?.id ?? null,
            colorName: l.color?.name ?? '',
            quantity: l.quantity,
            name: l.product.name,
            slug: l.product.slug,
            image: l.product.image,
            unitPrice: Number(l.unit_price),
          }
        })
        this._save()
      } catch {
        /* keep the local snapshot if the server is unreachable */
      }
    },
  },
})
