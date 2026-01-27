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
  const iconName = $derived(options.iconName || 'plus-sign')
  const classes = $derived(options.classes || 'me-2')
  const title = $derived(options.title || 'TITTEL MANGLER')
  const disabled = $derived<boolean>(options.disabled || false)
  const onClick = $derived(
    options.onClick ||
      (() => {
        console.warn('No onClick function provided')
      })
  )
</script>

<button
  {title}
  aria-label={title}
  class={`button-icon ${classes} ${disabled ? 'disabled' : ''}`}
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
  <pkt-icon name={iconName} variant="large" aria-hidden="true"></pkt-icon>
</button>

<style>
  .button-icon {
    width: 32px;
    height: 32px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    border: none;
    background-color: transparent;
  }

  .button-icon pkt-icon {
    width: 100%;
    height: 100%;
    background-color: transparent;
  }

  .disabled {
    cursor: not-allowed;
    --fg-color: var(--pkt-color-grays-gray-500);
    background-color: var(--pkt-color-grays-gray-100);
  }

  .button-icon:hover {
    background-color: var(--bs-gray);
  }

  .bordered {
    border: 1px solid var(--bs-gray);
    border-radius: 3px;
  }
</style>
