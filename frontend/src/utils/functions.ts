export function urlStringFrom(queryParams: { [key: string]: string }, path?: string): string {
  const prefix = path ? path + '?' : '?'
  return (
    prefix +
    Object.keys(queryParams)
      .map(key => key + '=' + queryParams[key])
      .join('&')
  )
}
