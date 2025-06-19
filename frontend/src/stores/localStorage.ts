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
