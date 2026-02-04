// Prefix for all cookies set by this application, to avoid cross-app conflicts on localhost
const cookiePrefix = 'mestring'

// Set a cookie by name and value, apply app prefix
export const setCookie = (name: string, value: string) => {
  const d = new Date()
  d.setTime(d.getTime() + 90 * 24 * 60 * 60 * 1000) // 90 days
  const expires = 'expires=' + d.toUTCString()
  document.cookie = `${cookiePrefix}_${name}=${value};${expires};path=/`
}

// Get a cookie value by name, apply app prefix
export const getCookie = (cookieName: string): string | null => {
  const cookiePairs = document.cookie.split(';')
  for (let i = 0; i < cookiePairs.length; i++) {
    const [name, value] = cookiePairs[i].trim().split('=', 2)
    if (`${cookiePrefix}_${cookieName}` === name) {
      return value
    }
  }
  return null
}
