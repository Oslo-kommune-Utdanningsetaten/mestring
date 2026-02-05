<script lang="ts">
  import { navigate } from 'svelte-tiny-router'
  import { trackPageView } from '../stores/analytics'
  import type { Snippet } from 'svelte'

  const { to, title, className, children, onclick } = $props<{
    to: string
    title?: string
    className?: string
    onclick?: (event: MouseEvent) => void
    children?: Snippet
  }>()

  const isExternal = $derived(to.startsWith('http'))

  const handleClick = (event: MouseEvent) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey) {
      // Allow opening in new tabs with modifier keys
      return
    }

    if (isExternal) {
      // External link, let the browser handle it
      return
    }

    event.preventDefault()

    // Allow Bootstrap dropdowns to close by letting the event bubble
    // Bootstrap listens for clicks on .dropdown-item elements
    requestAnimationFrame(() => {
      trackPageView(to)
      navigate(to)
    })
  }

  const onClickFunction = (event: MouseEvent) => {
    // First, call any custom click handler
    if (onclick) {
      onclick(event)

      // Respect handlers that prevent default behavior
      if (event.defaultPrevented) {
        return
      }
    }

    // Then perform the default navigation + tracking behavior
    handleClick(event)
  }
</script>

<a
  href={to}
  class={className}
  onclick={onClickFunction}
  target={isExternal ? '_blank' : '_self'}
  {title}
>
  {@render children?.()}
</a>
