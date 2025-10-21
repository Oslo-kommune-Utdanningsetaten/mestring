import type { MasteryConfigLevel, MasterySchemaConfig } from '../types/models'
import type { MasterySchemaType } from '../generated/types.gen'
import { isNumber } from './functions'

export type MasterySchemaWithConfig = MasterySchemaType & {
  config?: MasterySchemaConfig
}

export function useMasteryCalculations(masterySchema: MasterySchemaWithConfig | null) {
  const masteryLevels = masterySchema?.config?.levels || []
  const hasLevels = masteryLevels.length > 0

  const minValue = hasLevels ? Math.min(...masteryLevels.map(lev => lev.minValue)) : 0
  const maxValue = hasLevels ? Math.max(...masteryLevels.map(lev => lev.maxValue)) : 100
  const sliderValueIncrement = masterySchema?.config?.inputIncrement || 1
  const defaultValue = (minValue + maxValue) / 2

  const calculateSafeMasteryValue = (value: number | null | undefined): number => {
    let result: number = defaultValue
    if (value !== null && value !== undefined && isNumber(value)) {
      result = value
    }
    return Number(result.toFixed(0))
  }

  return {
    masteryLevels,
    minValue,
    maxValue,
    sliderValueIncrement,
    defaultValue,
    calculateSafeMasteryValue,
    hasLevels,
  }
}
