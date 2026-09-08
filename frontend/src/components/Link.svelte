<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'

  import { navigate } from 'svelte-tiny-router'
  import { trackPageView } from '../stores/analytics'
  import type { Snippet } from 'svelte'

  const { to, title, className, classes, iconName, children, onclick } = $props<{
    to: string
    title?: string
    className?: string
    classes?: string
    iconName?: string
    onclick?: (event: MouseEvent) => void
    children?: Snippet
  }>()

  const isExternal = $derived(to.startsWith('http'))
  const iconClasses = $derived(classes || className)

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

{#if iconName}
  <span class="button-icon-wrapper">
    <a
      href={to}
      class={`button-icon ${iconClasses || ''}`}
      onclick={onClickFunction}
      target={isExternal ? '_blank' : '_self'}
      {title}
      aria-label={title}
    >
      <pkt-icon name={iconName} variant="large" aria-hidden="true"></pkt-icon>
    </a>
  </span>
{:else}
  <a
    href={to}
    class={className}
    onclick={onClickFunction}
    target={isExternal ? '_blank' : '_self'}
    {title}
  >
    {@render children?.()}
  </a>
{/if}

<style>
  .button-icon-wrapper {
    display: inline-flex;
    align-items: center;
    gap: 0;
    vertical-align: top;
  }

  .button-icon {
    width: 32px;
    height: 32px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    padding: 5px;
    box-sizing: border-box;
    cursor: pointer;
    border: none;
    background-color: transparent;
  }

  .button-icon pkt-icon {
    width: 100%;
    height: 100%;
    background-color: transparent;
  }

  .button-icon:hover {
    background-color: var(--bs-gray);
  }

  .bordered {
    border: 1px solid var(--bs-gray);
    border-radius: 3px;
  }
</style>
