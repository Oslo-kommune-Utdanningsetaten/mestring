<script lang="ts">
  import { navigate } from 'svelte-tiny-router'

  export let to: string
  export let className: string = ''

  const handleClick = (event: MouseEvent) => {
    // Allow opening in new tabs with modifier keys
    if (event.ctrlKey || event.metaKey || event.shiftKey) {
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

<a href={to} class={className} onclick={handleClick}>
  <slot></slot>
</a>
