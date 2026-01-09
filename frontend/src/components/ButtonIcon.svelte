<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'

  interface Props {
    options: {
      iconName?: string
      classes?: string
      title?: string
      disabled?: boolean
      onClick?: () => void
    }
    children?: any
  }

  const { options }: Props = $props()
  const iconName = options.iconName || 'plus-sign'
  const classes = options.classes || 'me-2'
  const title = options.title || 'TITTEL MANGLER'
  const disabled = $derived<boolean>(options.disabled || false)
  const onClick =
    options.onClick ||
    (() => {
      console.warn('No onClick function provided')
    })
</script>

<button
  {title}
  aria-label={title}
  class={`button-icon ${classes}`}
  tabindex={disabled ? undefined : 0}
  onclick={() => !disabled && onClick()}
  onkeydown={(e: any) => {
    if (disabled) return
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onClick()
    }
  }}
  aria-disabled={disabled ? 'true' : 'false'}
>
  <pkt-icon name={iconName}></pkt-icon>
</button>

<style>
  .button-icon :global(pkt-icon),
  .button-icon:hover :global(pkt-icon),
  .button-icon:hover :global(pkt-icon svg) {
    border: none !important;
    width: 1.4em;
    height: 1.4em;
  }
  .button-icon {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    border: none;
    padding: 0.2rem;
    background-color: transparent;
  }

  .button-icon:hover {
    transform: scale(1);
    background-color: var(--bs-gray);
  }

  .bordered {
    border: 1px solid var(--bs-gray);
    border-radius: 3px;
  }
</style>
