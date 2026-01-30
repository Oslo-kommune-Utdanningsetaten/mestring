<script lang="ts">
  import { navigate } from 'svelte-tiny-router'
  import type { Snippet } from 'svelte'

  const { to, title, className, children, onclick } = $props<{
    to: string
    className?: string
    title?: string
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
      navigate(to)
    })
  }

  // if onclick is provided, use it; otherwise, use handleClick
  const onClickFunction = $derived(onclick || handleClick)
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
