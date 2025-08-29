declare module 'svelte-tiny-router' {
  import { SvelteComponentTyped } from 'svelte'

  export interface RouteProps {
    path?: string
    component?: any
  }

  export interface TinyRouter {
    path: string
    params: Record<string, string>
    query: Record<string, string>
    path: string
    getQueryParam(name: string): string | undefined
    hasQueryParam(name: string): boolean
    navigate(path: string): void
  }

  export class Router extends SvelteComponentTyped {}
  export class Route extends SvelteComponentTyped<RouteProps> {}
  export function navigate(path: string): void
  export function useTinyRouter(): TinyRouter
  export class Link extends SvelteComponentTyped<{ to: string }> {}
}
