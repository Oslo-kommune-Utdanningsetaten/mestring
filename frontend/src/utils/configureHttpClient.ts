import { client } from '../generated/client.gen'

const getCookie = (name: string): string | undefined => {
  if (typeof document === 'undefined') return undefined
  for (const entry of document.cookie.split('; ')) {
    const [key, ...rest] = entry.split('=')
    if (key === name) {
      const value = rest.join('=')
      return value ? decodeURIComponent(value) : undefined
    }
  }
  return undefined
}

client.interceptors.request.use(request => {
  const csrfToken = getCookie('csrftoken')
  if (csrfToken && !request.headers.has('X-CSRFTOKEN')) {
    request.headers.set('X-CSRFTOKEN', csrfToken)
  }
  return request
})
