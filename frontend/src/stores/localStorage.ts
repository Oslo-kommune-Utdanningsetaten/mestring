import { writable } from 'svelte/store'

const appKeyPrefix = 'mastery'
type T = string | number | boolean | Array<any> | object | null

const getKey = (key: string): string => {
  return [appKeyPrefix, key].join('-')
}

export const getLocalStorageItem = (key: string): T => {
  const item = localStorage.getItem(getKey(key))
  return item ? JSON.parse(item) : null
}

export const setLocalStorageItem = (key: string, item: T) => {
  localStorage.setItem(getKey(key), JSON.stringify(item))
}

export const removeLocalStorageItem = (key: string) => {
  localStorage.removeItem(getKey(key))
}

// Module-level cache — every call with the same key returns the same store instance,
// so all components that import it share a single reactive source of truth.
const storeCache = new Map<string, ReturnType<typeof writable>>()

export const localStorageStore = <V extends T>(key: string, defaultValue: V) => {
  if (!storeCache.has(key)) {
    const fullKey = getKey(key)
    const stored = localStorage.getItem(fullKey)
    const initial: V = stored !== null ? (JSON.parse(stored) as V) : defaultValue

    const store = writable<V>(initial)
    // Keep localStorage in sync on every write
    store.subscribe(value => localStorage.setItem(fullKey, JSON.stringify(value)))
    storeCache.set(key, store)
  }
  return storeCache.get(key)! as ReturnType<typeof writable<V>>
}
