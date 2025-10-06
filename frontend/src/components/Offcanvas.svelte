<script lang="ts">
  import type { Snippet } from 'svelte'

  interface OffcanvasProps {
    open?: boolean
    width?: string
    side?: 'right' | 'left'
    ariaLabel?: string
    onClosed?: () => void
    children?: Snippet
  }

  let {
    open = false,
    width = '50vw',
    side = 'right',
    ariaLabel = 'Panel',
    onClosed = () => {},
    children,
  }: OffcanvasProps = $props()

  type PanelState = 'closed' | 'opening' | 'open' | 'closing'
  let panelState = $state<PanelState>('closed')

  // State machine (panelState) depends on external `open` prop
  $effect(() => {
    if (open) {
      if (panelState === 'closed') {
        panelState = 'opening'
        // Double requestAnimationFrame to ensure mount + initial transform paint before switching to 'open'
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            if (open && panelState === 'opening') {
              panelState = 'open'
            }
          })
        })
      }
    } else {
      if (panelState === 'open' || panelState === 'opening') {
        panelState = 'closing'
      }
    }
  })

  function handleTransitionEnd(e: TransitionEvent) {
    if (e.propertyName !== 'transform') return
    if (panelState === 'closing') {
      panelState = 'closed'
      onClosed?.()
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (panelState === 'closed' || panelState === 'closing') return
    if (e.key === 'Escape') {
      e.stopPropagation()
      if (panelState === 'open' || panelState === 'opening') {
        panelState = 'closing'
      }
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if panelState !== 'closed'}
  <div
    class="offcanvas-panel {side} {panelState === 'open' ? 'is-active' : ''}"
    style:width
    role="dialog"
    aria-modal="true"
    aria-label={ariaLabel}
    tabindex="-1"
    ontransitionend={handleTransitionEnd}
  >
    {@render children?.()}
  </div>
{/if}

<style>
  .offcanvas-panel {
    position: fixed;
    top: 0;
    bottom: 0;
    background: #fff;
    z-index: 1050;
    overflow-y: auto;
    box-shadow: -10px 0px 20px 5px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    max-width: 100%;
    outline: none;
    transform: translateX(var(--initial-shift));
    transition: transform 260ms cubic-bezier(0.22, 0.61, 0.36, 1);
  }
  .offcanvas-panel.right {
    right: 0;
    --initial-shift: 100%;
  }
  .offcanvas-panel.left {
    left: 0;
    --initial-shift: -100%;
  }
  .offcanvas-panel.is-active {
    transform: translateX(0);
  }

  @media (max-width: 900px) {
    .offcanvas-panel {
      width: min(100vw, 600px);
    }
  }
</style>
