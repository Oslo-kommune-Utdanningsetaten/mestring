class LocalStore<T> {
  value = $state<T>() as T
  key = ''
  keyPrefix = 'mastery-'

  constructor(key: string, value: T) {
    this.key = key
    this.value = value
    const item = localStorage.getItem(`${this.keyPrefix}${key}`)
    if (item) {
      this.value = this.deserialize(item)
    }

    $effect(() => {
      localStorage.setItem(`${this.keyPrefix}${key}`, this.serialize(this.value))
    })
  }

  serialize(value: T): string {
    return JSON.stringify(value)
  }

  deserialize(item: string): T {
    return JSON.parse(item)
  }
}

export function localStore<T>(key: string, value: T) {
  return new LocalStore(key, value)
}
