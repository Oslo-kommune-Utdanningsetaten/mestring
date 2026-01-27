<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'

  interface Props {
    options: {
      iconName?: string
      classes?: string
      title?: string
      variant?: string
      skin?: string
      color?: string
      disabled?: boolean
      onClick?: () => void
      size?: 'tiny' | 'small' | 'medium' | 'large'
    }
    children?: any
  }

  const { options, children }: Props = $props()
  const size = options.size || 'small'
  const isTiny = size === 'tiny'
  const iconName = options.iconName || 'plus-sign'
  const classes = options.classes || 'me-2'
  const title = options.title || 'TITTEL MANGLER'
  const variant = options.variant || 'icon-only'
  const skin = options.skin || 'tertiary'
  const color = options.color || null // allowed colors defined here https://punkt.oslo.kommune.no/latest/komponenter-og-maler/komponenter/button/#props
  const disabled = $derived<boolean>(options.disabled || false)
  const onClick =
    options.onClick ||
    (() => {
      console.warn('No onClick function provided')
    })
</script>

{#if isTiny}
  <pkt-icon
    name={iconName}
    {title}
    aria-label={title}
    class={`mini-icon-button ${classes}`}
    role="button"
    tabindex={disabled ? undefined : '0'}
    onclick={() => !disabled && onClick()}
    onkeydown={(e: any) => {
      if (disabled) return
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        onClick()
      }
    }}
    aria-disabled={disabled ? 'true' : 'false'}
  ></pkt-icon>
{:else}
  <pkt-button
    size={size === 'medium' || size === 'large' ? size : 'small'}
    {skin}
    type="button"
    {variant}
    class={classes}
    {iconName}
    {color}
    onclick={() => onClick()}
    {disabled}
    onkeydown={(e: any) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        onClick()
      }
    }}
    role="button"
    tabindex="0"
  >
    {#if children}
      {@render children()}
    {:else}
      {title}
    {/if}
  </pkt-button>
{/if}

<style>
  :global(pkt-button.justify-end) {
    justify-self: end;
  }

  :global(pkt-button.justify-start) {
    justify-self: start;
  }

  /* Tiny icon mode */
  :global(.mini-icon-button) {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    width: 1.2rem;
    height: 1.2rem;
    cursor: pointer;
    transition:
      filter 0.15s ease-in-out,
      transform 0.15s ease-in-out;
  }
  :global(.mini-icon-button:hover) {
    filter: drop-shadow(0 0 6px var(--bs-primary-hover));
    transform: scale(1.2);
    border-radius: 50%;
    background-color: rgba(0, 123, 255, 0.08);
  }
  :global(.mini-icon-button[aria-disabled='true']),
  :global(.mini-icon-button[aria-disabled='true']:hover) {
    opacity: 0.5;
    cursor: not-allowed;
    filter: none;
    transform: none;
    background: none;
  }
</style>
