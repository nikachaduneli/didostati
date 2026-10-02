import { lang } from './i18n'

export class ApiError extends Error {
  constructor(data, status) {
    super(typeof data?.detail === 'string' ? data.detail : 'Request failed')
    this.data = data
    this.status = status
  }
  /** Flatten DRF validation errors to one readable string. */
  get text() {
    const d = this.data
    if (!d || typeof d !== 'object') return this.message
    return Object.entries(d)
      .map(([k, v]) => {
        const msg = Array.isArray(v) ? v.join(' ') : typeof v === 'string' ? v : JSON.stringify(v)
        return k === 'detail' || k === 'non_field_errors' ? msg : `${k.replace('_', ' ')}: ${msg}`
      })
      .join(' · ')
  }
}

export async function api(path, { method = 'GET', body, params } = {}) {
  let url = '/api' + path
  if (params) {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== '' && v != null))
    if ([...qs].length) url += '?' + qs
  }
  const headers = { 'X-Lang': lang.value }
  if (body) headers['Content-Type'] = 'application/json'
  const token = localStorage.getItem('token')
  if (token) headers.Authorization = 'Token ' + token
  const res = await fetch(url, { method, headers, body: body ? JSON.stringify(body) : undefined })
  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new ApiError(data, res.status)
  return data
}
