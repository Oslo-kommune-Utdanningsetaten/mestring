const appKeyPrefix = 'mastery'
type T = string | number | boolean | Array<any> | object | null

function getKey(key: string): string {
  return [appKeyPrefix, key].join('-')
}

export function getLocalStorageItem(key: string): T {
  const item = localStorage.getItem(getKey(key))
  return item ? JSON.parse(item) : null
}

export function setLocalStorageItem(key: string, item: T) {
  localStorage.setItem(getKey(key), JSON.stringify(item))
}
