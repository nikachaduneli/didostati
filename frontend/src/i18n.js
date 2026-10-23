import { ref } from 'vue'
import ka from './locales/ka'

const KEY = 'lang'
const saved = (() => {
  try {
    return localStorage.getItem(KEY)
  } catch {
    return null
  }
})()
// Georgian pages live under /ka, English ones have no prefix (search engines index both).
const PREFIX = /^\/ka(?=[/?#]|$)/

/** '/ka/shop?x' -> '/shop?x', '/ka' -> '/'. */
export const stripLang = (path) => path.replace(PREFIX, '').replace(/^(?=[?#]|$)/, '/')

/** The address of `path` in language `code`: '/shop' -> '/ka/shop' for Georgian. */
export function withLang(path, code = lang.value) {
  const p = stripLang(path)
  if (code !== 'ka') return p
  return '/ka' + (/^\/(?=[?#]|$)/.test(p) ? p.slice(1) : p)
}

const initial = PREFIX.test(location.pathname)
  ? 'ka'
  : saved || ((navigator.language || '').toLowerCase().startsWith('ka') ? 'ka' : 'en')

export const lang = ref(initial === 'ka' ? 'ka' : 'en')
document.documentElement.lang = lang.value

export function setLang(code) {
  lang.value = code
  document.documentElement.lang = code
  try {
    localStorage.setItem(KEY, code)
  } catch {}
}

/** Translate an English string (the key); `{name}` placeholders are filled from `params`. */
export function t(text, params) {
  let s = (lang.value === 'ka' && ka[text]) || text
  if (params) for (const [k, v] of Object.entries(params)) s = s.replaceAll(`{${k}}`, v)
  return s
}

export const locale = () => (lang.value === 'ka' ? 'ka-GE' : 'en-GB')
export const fdate = (d) => new Date(d).toLocaleDateString(locale())
