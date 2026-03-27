import { get, writable } from 'svelte/store'

const appKeyPrefix = 'mastery'
type StorableValue = string | number | boolean | Array<any> | object | null

const getKey = (key: string): string => [appKeyPrefix, key].join('-')

export type LocalStorageStore<Value> = {
  subscribe: ReturnType<typeof writable<Value>>['subscribe']
  set: (value: Value) => void
  get: () => Value
  remove: () => void
}

// Module-level cache — every call with the same key returns the same store instance,
// so all components that import it share a single reactive source of truth
const cache = new Map<string, LocalStorageStore<any>>()

const localStorageStore = <Value extends StorableValue>(
  key: string
): LocalStorageStore<Value | null> => {
  if (!cache.has(key)) {
    const fullKey = getKey(key)
    const stored = localStorage.getItem(fullKey)
    const initial: Value | null = stored !== null ? (JSON.parse(stored) as Value) : null

    const store = writable<Value | null>(initial)

    const instance: LocalStorageStore<Value | null> = {
      subscribe: store.subscribe,
      set: (value: Value | null) => {
        localStorage.setItem(fullKey, JSON.stringify(value))
        store.set(value)
      },
      get: () => get(store),
      remove: () => {
        localStorage.removeItem(fullKey)
        store.set(null)
      },
    }
    cache.set(key, instance)
  }
  return cache.get(key)! as LocalStorageStore<Value | null>
}

export { localStorageStore as localStorage }
