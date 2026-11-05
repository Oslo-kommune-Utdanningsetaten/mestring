<script lang="ts">
  import Sortable, { type SortableEvent } from 'sortablejs'
  import type { SubjectType, GroupType, TagCollectionType } from '../generated/types.gen'
  import {
    subjectsRetrieve,
    groupsList,
    tagCollectionsList,
    tagCollectionsPartialUpdate,
    tagCollectionsCreate,
  } from '../generated/sdk.gen'
  import { currentSchool } from '../stores/data'
  import { hasUserAccessToFeature } from '../stores/access'

  import GroupTag from '../components/GroupTag.svelte'
  import ButtonMini from '../components/ButtonMini.svelte'

  const { subjectId }: { subjectId: string } = $props()

  const maxTagLength = 50
  let subject = $state<SubjectType | undefined>(undefined)
  let groups = $state<GroupType[]>([])
  let tagCollection = $state<TagCollectionType | undefined>(undefined)

  let sortableInstance: Sortable | null = null
  let tagInputElement = $state<HTMLInputElement | null>(null)
  let tagsListElement = $state<HTMLElement | null>(null)
  let newTagValue = $state<string | undefined>(undefined)
  let isNewTagDuplicate = $derived.by(() => {
    return (tagCollection?.tags as string[])?.includes(newTagValue ?? '') ?? false
  })
  let isNewTagTooLong = $derived.by(() => {
    return (newTagValue?.length ?? 0) > maxTagLength
  })

  const fetchSubjectData = async () => {
    try {
      const subjectResult = await subjectsRetrieve({ path: { id: subjectId } })
      subject = subjectResult.data!
      if (!subject) return

      // fetch adjoined groups
      const groupsResult = await groupsList({
        query: { subject: subjectId, school: $currentSchool.id },
      })
      groups = groupsResult.data ?? []
      await fetchTags()
    } catch (error) {
      console.error(`Could not load data for subject ${subjectId}`, error)
    }
  }

  const fetchTags = async () => {
    if (!subject) return
    try {
      const tagCollectionResult = await tagCollectionsList({
        query: { subject: subjectId, school: $currentSchool.id },
      })
      tagCollection = (tagCollectionResult.data || [])[0] as TagCollectionType | undefined
    } catch (error) {
      console.error(`Could not fetch tags for subject ${subjectId}`, error)
    }
  }

  const handleAddTag = async (tag: string | undefined) => {
    if (!tag || tag.trim() === '' || !tagInputElement) return
    if (tagCollection) {
      // update existing tag collection with new tag
      const existingTags = (tagCollection.tags as string[] | undefined) ?? []
      const updatedTags = [...existingTags, tag]
      try {
        const result = await tagCollectionsPartialUpdate({
          path: { id: tagCollection.id },
          body: { tags: updatedTags },
        })
        tagCollection = result.data!
        newTagValue = undefined
      } catch (error) {
        console.error(`Could not add tag ${tag}`, error)
      }
    } else {
      // create new tag collection with the tag
      try {
        const result = await tagCollectionsCreate({
          body: {
            subjectId: subjectId,
            schoolId: $currentSchool.id,
            tags: [tag],
          },
        })
        tagCollection = result.data!
        newTagValue = undefined
      } catch (error) {
        console.error(`Could not create tag collection with tag ${tag}`, error)
      }
    }
  }

  const handleTagOrderChange = async (event: SortableEvent) => {
    if (!tagCollection) return
    const { oldIndex, newIndex } = event
    if (oldIndex === undefined || newIndex === undefined) return

    const localTags = (tagCollection.tags || []) as string[]
    // Remove moved tag and capture it
    const [movedTag] = localTags.splice(oldIndex, 1)
    // Insert moved tag at new index
    localTags.splice(newIndex, 0, movedTag)
    try {
      const result = await tagCollectionsPartialUpdate({
        path: { id: tagCollection.id },
        body: { tags: localTags },
      })
      tagCollection = result.data!
    } catch (error) {
      console.error(`Could not update tag order`, error)
    }
  }

  const handleTagDelete = async (index: number) => {
    if (!tagCollection) return
    const updatedTags = (tagCollection.tags as string[] | undefined) ?? []
    updatedTags.splice(index, 1)
    try {
      const result = await tagCollectionsPartialUpdate({
        path: { id: tagCollection.id },
        body: { tags: updatedTags },
      })
      tagCollection = result.data!
    } catch (error) {
      console.error(`Could not delete tag at index ${index}`, error)
    }
  }

  $effect(() => {
    fetchSubjectData()
  })

  $effect(() => {
    if (tagInputElement) {
      tagInputElement.focus()
    }
  })

  $effect(() => {
    if (tagsListElement) {
      sortableInstance = new Sortable(tagsListElement, {
        animation: 150,
        handle: '.row-handle-draggable',
        onEnd: handleTagOrderChange,
      })
    }
    return () => {
      // clean up if element unmounts
      if (!tagsListElement && sortableInstance) {
        sortableInstance.destroy()
        sortableInstance = null
      }
    }
  })
</script>

<section class="py-3">
  {#if subject}
    <!-- Header info-->
    <div class="mb-5">
      <h2 class="mb-1">
        {subject.shortName}
      </h2>
      <div class="text-secondary mb-1" title="Fullt navn på faget">
        {subject.displayName}
      </div>
      <div class="text-secondary" title="Grepkode">
        Grepkode: {subject.grepCode}
      </div>
    </div>

    <!-- Groups-->
    <div class="mb-5">
      <h3 class="mb-3">Grupper som tilhører faget</h3>
      {#if groups.length > 0}
        <div class="d-flex align-items-center gap-3">
          {#each groups as group}
            <GroupTag
              {group}
              href="/groups/{group.id}"
              isGroupNameEnabled={true}
              isIconEnabled={true}
            />
          {/each}
        </div>
      {:else}
        Ingen grupper tilgjengelig
      {/if}
    </div>

    <!-- Tags-->
    <div>
      <h3 class="mb-3">Tags som tilhører faget</h3>
      {#if tagCollection}
        <div bind:this={tagsListElement} class="list-tag">
          {#each (tagCollection?.tags ?? []) as string[] as tag, index}
            {#key tag}
              <div class="list-group-item tag-row">
                <span>
                  {#if $hasUserAccessToFeature( 'tagCollection', 'update', { subjectId: subject.id } )}
                    <pkt-icon
                      title="Endre rekkefølge"
                      class="me-2 row-handle-draggable"
                      name="drag"
                      role="button"
                      tabindex="0"
                    ></pkt-icon>
                  {/if}
                </span>
                <span>
                  {tag}
                </span>
                <span class="pt-2">
                  {#if $hasUserAccessToFeature( 'tagCollection', 'update', { subjectId: subject.id } )}
                    <ButtonMini
                      options={{
                        title: 'Slett tag',
                        iconName: 'trash-can',
                        skin: 'tertiary',
                        variant: 'icon-only',
                        size: 'tiny',
                        onClick: () => handleTagDelete(index),
                      }}
                    />
                  {/if}
                </span>
              </div>
            {/key}
          {/each}
        </div>
      {:else}
        <p class="text-muted">
          Ingen tags tilgjengelig på dette faget.
          {#if $hasUserAccessToFeature('tagCollection', 'create', { subjectId: subject.id })}
            Men kanskje du vil legge til noen?
          {/if}
        </p>
      {/if}
      <div class="mt-3">
        {#if $hasUserAccessToFeature('tagCollection', 'update', { subjectId: subject.id })}
          <label for="newTagInput" class="form-label visually-hidden">Ny tag</label>
          <input
            id="newTagInput"
            type="text"
            class="form-control rounded-0 border-2 border-primary input-field mb-2"
            name="displayName"
            bind:this={tagInputElement}
            bind:value={newTagValue}
            placeholder="Ny tag"
            onkeydown={(event: KeyboardEvent) => {
              if (event.key === 'Enter' && !isNewTagDuplicate && !isNewTagTooLong)
                handleAddTag(newTagValue)
            }}
          />
          {#if isNewTagDuplicate}
            <p class="text-danger">Denne taggen finnes allerede</p>
          {/if}
          <p class="text-muted">
            {newTagValue?.length ?? 0}/{maxTagLength}
            {#if isNewTagTooLong}<span class="text-danger">
                For lang, for lang, den tag er for lang. Hilsen Det Kongelige Norske Tagdepartement.
              </span>{/if}
          </p>

          <ButtonMini
            options={{
              title: 'Legg til ny tag',
              iconName: 'plus-sign',
              skin: 'primary',
              variant: 'icon-left',
              disabled: !newTagValue?.trim() || isNewTagDuplicate || isNewTagTooLong,
              onClick: () => handleAddTag(newTagValue),
            }}
          >
            Legg til
          </ButtonMini>
        {/if}
      </div>
    </div>
  {:else}
    <div class="m-2">Fant ikke faget</div>
  {/if}
</section>

<style>
  .list-tag {
    width: fit-content;
    min-width: 25%;
    max-width: 100%;
  }
  .tag-row {
    display: grid;
    grid-template-columns: auto 1fr auto;
    column-gap: 5px;
    background-color: var(--bs-light);
    min-height: 3rem;
    align-items: center;
    border: 1px solid var(--bs-border-color);
  }
  .tag-row:first-child {
    border-top-left-radius: var(--bs-border-radius);
    border-top-right-radius: var(--bs-border-radius);
  }
  .tag-row:last-child {
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
