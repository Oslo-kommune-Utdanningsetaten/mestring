import { derived, get } from 'svelte/store'
import { currentSchool } from './data'

const defaultTranslations: Record<string, string> = {
  'a goal': 'mål',
  'the goal': 'målet',
  goals: 'mål',
  'the goals': 'målene',
  'an observation': 'observasjon',
  'the observation': 'observasjonen',
  observations: 'observasjoner',
  'the observations': 'observasjonene',
}

const schoolUITranslations = derived(
  currentSchool,
  $currentSchool => $currentSchool?.uiTranslations ?? {}
)

const capitalizeString = (item: string): string => {
  return item.charAt(0).toUpperCase() + item.slice(1)
}

// Accepts a key and options, returns a school-specific or default translated string, or the key itself if no translation is found
export const t = (key: string, options: Record<string, any> | undefined = {}) => {
  if (!key) throw new Error('Translation key is required')
  const schoolTranslations = get(schoolUITranslations)
  let result: string

  // try school-specific translations
  if (schoolTranslations[key]) {
    result = schoolTranslations[key]
  } else if (defaultTranslations[key]) {
    // fall back to default translations
    result = defaultTranslations[key]
  } else {
    // if no translation is found, use key itself
    result = key
  }

  if (options.capitalize) {
    result = capitalizeString(result)
  }
  return result
}
