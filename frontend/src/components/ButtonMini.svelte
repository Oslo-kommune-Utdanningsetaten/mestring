<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'

  interface Props {
    options: {
      iconName?: string
      classes?: string
      title?: string
      onClick?: () => void
      variant?: string
      skin?: string
    }
    children?: any
  }

  const { options, children }: Props = $props()
  const iconName = options.iconName || 'plus-sign'
  const classes = options.classes || 'mini-button bordered'
  const title = options.title || 'TITTEL MANGLER'
  const variant = options.variant || 'icon-only'
  const skin = options.skin || 'tertiary'
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
