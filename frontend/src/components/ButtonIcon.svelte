<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import DelayedAction from './DelayedAction.svelte'

  interface Props {
    options: {
      iconName?: string
      classes?: string
      title?: string
      disabled?: boolean
      onClick?: () => void
      delayActionFor?: number
      delayActionTitle?: string
    }
    children?: any
  }

  const { options }: Props = $props()
  const iconName = $derived(options.iconName || 'plus-sign')
  const classes = $derived(options.classes || 'me-2')
  const title = $derived(options.title || 'TITTEL MANGLER')
  const disabled = $derived<boolean>(options.disabled || false)
  const delayActionFor = $derived(options.delayActionFor)

  let hasBeenClicked = $state(false)

  const onClick = $derived(
    options.onClick ||
      (() => {
        console.warn('No onClick function provided')
      })
  )

  const handleClick = () => {
    if (disabled) return
    if (delayActionFor) {
      // onClick will be executed after delay
      hasBeenClicked = true
    } else {
      // Execute onClick immediately
      onClick()
    }
  }

  const handleAbort = () => {
    hasBeenClicked = false
  }
</script>

<div class="button-icon-wrapper">
  <button
    {title}
    aria-label={title}
    class={`button-icon ${classes} ${disabled ? 'disabled' : ''}`}
    tabindex={disabled ? undefined : 0}
    onclick={handleClick}
    onkeydown={(e: any) => {
      if (disabled) return
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        handleClick()
      }
    }}
    aria-disabled={disabled ? 'true' : 'false'}
  >
    <pkt-icon name={iconName} variant="large" aria-hidden="true"></pkt-icon>
  </button>
  {#if delayActionFor && hasBeenClicked}
    <DelayedAction onAction={onClick} onAbort={handleAbort} delay={delayActionFor} />
  {/if}
</div>

<style>
  .button-icon-wrapper {
    display: inline-flex;
    align-items: center;
    gap: 0;
  }

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
