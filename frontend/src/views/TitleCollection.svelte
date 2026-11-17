<script lang="ts">
  import uniq from 'lodash/uniq'
  import Sortable, { type SortableEvent } from 'sortablejs'
  import type { TitleCollectionType } from '../generated/types.gen'
  import {
    titleCollectionsRetrieve,
    titleCollectionsList,
    titleCollectionsPartialUpdate,
    titleCollectionsCreate,
  } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import { hasUserAccessToFeature } from '../stores/access'
  import { t } from '../stores/translations'

  import ButtonMini from '../components/ButtonMini.svelte'
  import ButtonIcon from '../components/ButtonIcon.svelte'

  const { titleCollectionId }: { titleCollectionId: string } = $props()

  const maxTitleLength = 200
  let titleCollection = $state<TitleCollectionType | undefined>(undefined)

  let sortableInstance: Sortable | null = null
  let titleTextInputElement = $state<HTMLInputElement | null>(null)
  let titleTextAreaElement = $state<HTMLTextAreaElement | null>(null)
  let titlesListElement = $state<HTMLElement | null>(null)
  let isTextAreaInputEnabled = $state<boolean>(false)
  let newTitleValue = $state<string | undefined>(undefined)

  const schoolId = $derived($dataStore.currentSchool?.id)

  let isNewTitleDuplicate = $derived.by(() => {
    return (titleCollection?.titles as string[])?.includes(newTitleValue ?? '') ?? false
  })

  let isNewTitleTooLong = $derived.by(() => {
    return (newTitleValue?.length ?? 0) > maxTitleLength
  })

  const fetchData = async () => {
    let collection = undefined
    try {
      if (titleCollectionId) {
        // fetch by id
        const result = await titleCollectionsRetrieve({ path: { id: titleCollectionId } })
        collection = result.data!
      } else {
        // fetch first we find for this school
        const listResult = await titleCollectionsList({ query: { school: schoolId } })
        collection = listResult.data?.[0]
      }
      if (!collection && !titleCollectionId) {
        // if no specific collection requested and there is none, create a new one
        const createResult = await titleCollectionsCreate({
          body: { schoolId: schoolId, titles: [] },
        })
        collection = createResult.data!
      }
    } catch (error) {
      console.error(`Could not fetch or create title collection`, error)
    } finally {
      titleCollection = collection
    }
  }

  const handleAddTitle = async (input: string | undefined) => {
    if (!titleCollection || !input || input.trim() === '') return

    const existingTitles = (titleCollection.titles as string[] | undefined) ?? []
    const newTitles = input
      .split('\n')
      .map(t => t.trim())
      .filter(t => t !== '')
    const titles = uniq([...existingTitles, ...newTitles])

    try {
      const result = await titleCollectionsPartialUpdate({
        path: { id: titleCollection.id },
        body: { titles },
      })
      titleCollection = result.data!
      newTitleValue = undefined
    } catch (error) {
      console.error(`Could not add ${input}`, error)
    }
  }

  const handleTitleOrderChange = async (event: SortableEvent) => {
    if (!titleCollection) return
    const { oldIndex, newIndex } = event
    if (oldIndex === undefined || newIndex === undefined) return

    const localTitles = [...((titleCollection.titles || []) as string[])]
    // Remove moved title and capture it
    const [movedTitle] = localTitles.splice(oldIndex, 1)
    // Insert moved title at new index
    localTitles.splice(newIndex, 0, movedTitle)
    try {
      const result = await titleCollectionsPartialUpdate({
        path: { id: titleCollection.id },
        body: { titles: localTitles },
      })
      titleCollection = result.data!
    } catch (error) {
      console.error(`Could not update title order`, error)
    }
  }

  const handleTitleDelete = async (index: number) => {
    if (!titleCollection) return
    const updatedTitles = [...((titleCollection.titles as string[] | undefined) ?? [])]
    updatedTitles.splice(index, 1)
    try {
      const result = await titleCollectionsPartialUpdate({
        path: { id: titleCollection.id },
        body: { titles: updatedTitles },
      })
      titleCollection = result.data!
    } catch (error) {
      console.error(`Could not delete title at index ${index}`, error)
    }
  }

  const handleSortTitles = async () => {
    if (!titleCollection) return
    const sortedTitles = [...((titleCollection.titles as string[] | undefined) ?? [])].sort()
    try {
      const result = await titleCollectionsPartialUpdate({
        path: { id: titleCollection.id },
        body: { titles: sortedTitles },
      })
      titleCollection = result.data!
    } catch (error) {
      console.error(`Could not sort titles`, error)
    }
  }

  $effect(() => {
    if (schoolId) fetchData()
  })

  $effect(() => {
    if (isTextAreaInputEnabled) {
      titleTextAreaElement && titleTextAreaElement.focus()
    } else {
      titleTextInputElement && titleTextInputElement.focus()
    }
  })

  $effect(() => {
    if (titlesListElement) {
      sortableInstance = new Sortable(titlesListElement, {
        animation: 150,
        handle: '.row-handle-draggable',
        onEnd: handleTitleOrderChange,
      })
    }
    return () => {
      // clean up if element unmounts
      if (!titlesListElement && sortableInstance) {
        sortableInstance.destroy()
        sortableInstance = null
      }
    }
  })
</script>

<section class="py-3">
  {#if titleCollection}
    <!-- Header info-->
    <h2 class="mb-3">{t('titleRepository', { form: 'sin-indef', capitalize: true })}</h2>

    <!-- Titles-->
    <div>
      <p>
        Her kan du vedlikeholde en liste av {t('goal', {
          form: 'sin-indef',
          capitalize: false,
        })}-titler slik at det blir enklere for lærerne å opprette mål.
      </p>
      <div class="my-3">
        {#if $hasUserAccessToFeature('titleCollection', 'update', {})}
          <div class="d-flex align-items-start gap-2 mb-2">
            <!-- Text area input -->
            {#if isTextAreaInputEnabled}
              <label for="newTitlesInput" class="form-label visually-hidden">Nye mål</label>
              <div class="input-wrapper">
                <textarea
                  id="newTitlesInput"
                  class="form-control rounded-0 border-2 border-primary"
                  bind:this={titleTextAreaElement}
                  bind:value={newTitleValue}
                  placeholder="Linjeskift-separert liste med titler"
                  rows="5"></textarea>
                <div class="input-corner-button">
                  <ButtonIcon
                    options={{
                      title: 'Minimer område',
                      iconName: 'minimize',
                      onClick: () => (isTextAreaInputEnabled = false),
                    }}
                  ></ButtonIcon>
                </div>
              </div>
              <ButtonMini
                options={{
                  title: 'Legg til nye titler',
                  iconName: 'plus-sign',
                  skin: 'primary',
                  variant: 'icon-left',
                  disabled: !newTitleValue?.trim(),
                  onClick: () => handleAddTitle(newTitleValue),
                }}
              >
                Legg til
              </ButtonMini>
            {:else}
              <!-- Single line input -->
              <label for="newTitleInput" class="form-label visually-hidden">Nytt mål</label>
              <div class="input-wrapper">
                <input
                  id="newTitleInput"
                  type="text"
                  class="form-control rounded-0 border-2 border-primary mb-2"
                  name="displayName"
                  bind:this={titleTextInputElement}
                  bind:value={newTitleValue}
                  placeholder="Ny tittel"
                  onkeydown={(event: KeyboardEvent) => {
                    if (event.key === 'Enter' && !isNewTitleDuplicate && !isNewTitleTooLong)
                      handleAddTitle(newTitleValue)
                  }}
                />
                <div class="input-corner-button">
                  <ButtonIcon
                    options={{
                      title: 'Utvid område',
                      iconName: 'expand',
                      onClick: () => (isTextAreaInputEnabled = true),
                    }}
                  ></ButtonIcon>
                </div>
              </div>
              <ButtonMini
                options={{
                  title: 'Legg til ny tittel',
                  iconName: 'plus-sign',
                  skin: 'primary',
                  variant: 'icon-left',
                  disabled: !newTitleValue?.trim() || isNewTitleDuplicate || isNewTitleTooLong,
                  onClick: () => handleAddTitle(newTitleValue),
                }}
              >
                Legg til
              </ButtonMini>
            {/if}
          </div>

          {#if !isTextAreaInputEnabled}
            {#if isNewTitleDuplicate}
              <p class="text-danger">Denne tittelen finnes allerede</p>
            {/if}

            <p class="text-muted">
              {newTitleValue?.length ?? 0}/{maxTitleLength}
              {#if isNewTitleTooLong}
                <span class="text-danger">
                  For lang, for lang, den tittel er for lang. Det Kongelige Norske
                  Titteledepartement.
                </span>
              {/if}
            </p>
          {/if}
        {/if}
      </div>

      <ButtonMini
        options={{
          title: 'Sortér alfabetisk',
          iconName: 'arrow-down-up',
          skin: 'primary',
          variant: 'icon-left',
          classes: 'mb-2',
          onClick: () => handleSortTitles(),
        }}
      >
        Sortér alfabetisk
      </ButtonMini>

      <div bind:this={titlesListElement} class="list-title">
        {#each (titleCollection?.titles ?? []) as string[] as title, index}
          {#key title}
            <div class="list-group-item title-row">
              <span>
                {#if $hasUserAccessToFeature('titleCollection', 'update', {})}
                  <pkt-icon
                    title="Endre rekkefølge"
                    class="me-2 mt-1 ms-1 row-handle-draggable"
                    name="drag"
                    role="button"
                    tabindex="0"
                  ></pkt-icon>
                {/if}
              </span>
              <span>
                {title}
              </span>
              <span class="pt-2">
                {#if $hasUserAccessToFeature('titleCollection', 'update', {})}
                  <ButtonMini
                    options={{
                      title: 'Slett title',
                      iconName: 'trash-can',
                      skin: 'tertiary',
                      variant: 'icon-only',
                      size: 'tiny',
                      onClick: () => handleTitleDelete(index),
                    }}
                  />
                {/if}
              </span>
            </div>
          {/key}
        {/each}
      </div>
    </div>
  {:else}
    <div class="m-2">Fant ikke greia</div>
  {/if}
</section>

<style>
  .input-wrapper {
    position: relative;
    width: 50%;
    min-width: 20rem;
  }

  .input-corner-button {
    position: absolute;
    top: 0.25rem;
    right: 0.25rem;
  }

  .list-title {
    width: fit-content;
    min-width: 25%;
    max-width: 100%;
  }

  .title-row {
    display: grid;
    grid-template-columns: auto 1fr auto;
    column-gap: 5px;
    background-color: var(--bs-light);
    min-height: 3rem;
    align-items: center;
    border: 1px solid var(--bs-border-color);
  }

  .title-row:first-child {
    border-top-left-radius: var(--bs-border-radius);
    border-top-right-radius: var(--bs-border-radius);
  }

  .title-row:last-child {
    border-bottom-left-radius: var(--bs-border-radius);
    border-bottom-right-radius: var(--bs-border-radius);
  }

  .row-handle-draggable {
    cursor: move;
    vertical-align: -8%;
    width: 1.5rem;
    height: 1.5rem;
  }
</style>
