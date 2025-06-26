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
    navigate(to)
  }
</script>

<a href={to} class={className} onclick={handleClick}>
  <slot></slot>
</a>
