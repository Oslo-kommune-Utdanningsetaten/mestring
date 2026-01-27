<script lang="ts">
  import { navigate } from 'svelte-tiny-router'

  export let to: string
  export let className: string = ''
  const isExternal = to.startsWith('http')

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
</script>

<a href={to} class={className} onclick={handleClick} target={isExternal ? '_blank' : '_self'}>
  <slot></slot>
</a>
