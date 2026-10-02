import { locale } from './i18n'

export const CURRENCY = 'GEL'
export const money = (v) => new Intl.NumberFormat(locale(), { style: 'currency', currency: CURRENCY }).format(Number(v))
