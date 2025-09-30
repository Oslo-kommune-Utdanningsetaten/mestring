<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'

  interface Props {
    options: {
      iconName?: string
      classes?: string
      title?: string
      variant?: string
      skin?: string
      disabled?: boolean
      onClick?: () => void
    }
    children?: any
  }

  const { options, children }: Props = $props()
  const iconName = options.iconName || 'plus-sign'
  const classes = options.classes || 'me-2'
  const title = options.title || 'TITTEL MANGLER'
  const variant = options.variant || 'icon-only'
  const skin = options.skin || 'tertiary'
  const disabled = $derived<boolean>(options.disabled || false)
  const onClick =
    options.onClick ||
    (() => {
      console.warn('No onClick function provided')
    })
</script>

<pkt-button
  size="small"
  {skin}
  type="button"
  {variant}
  class={classes}
  {iconName}
  {title}
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

<style>
  :global(pkt-button.justify-end) {
    justify-self: end;
  }

  :global(pkt-button.justify-start) {
    justify-self: start;
  }
</style>
