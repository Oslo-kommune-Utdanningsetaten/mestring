// prefix cookies set by this application, to avoid cross-app conflicts on localhost
const cookiePrefix = 'mestring'

// set a cookie by name and value, add prefix
export const setCookie = (name: string, value: string) => {
  const d = new Date()
  d.setTime(d.getTime() + 90 * 60 * 60 * 1000) // 90 days
  const expires = 'expires=' + d.toUTCString()
  document.cookie = `${cookiePrefix}_${name}=${value};${expires};path=/`
}

// get a cookie by name, use prefix
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
