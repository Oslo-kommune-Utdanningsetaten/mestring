import type { MasterySchemaWithConfig, MasteryConfigLevel } from '../types/models'
import { isNumber } from './functions'

export const getMasteryLevelColorByValue = (
  value: number,
  masterySchema: MasterySchemaWithConfig,
  opacity?: number
): string => {
  const masteryLevels = masterySchema.config?.levels || []
  const masteryLevel = masteryLevels.find(ml => ml.minValue <= value && ml.maxValue >= value)
  let color = masteryLevel ? masteryLevel.color : `rgba(100, 100, 100)`
  if (!opacity) {
    return color
  }
  const opacityValue = opacity || 1
  // Extract the RGB values and construct a new RGBA string with the provided opacity
  const rgbaMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/)
  const hexMatch = color.match(/#([0-9a-fA-F]{6})/)
  if (rgbaMatch) {
    const r = rgbaMatch[1]
    const g = rgbaMatch[2]
    const b = rgbaMatch[3]
    color = `rgba(${r}, ${g}, ${b}, ${opacityValue})`
  } else if (hexMatch) {
    const hex = hexMatch[1]
    const r = parseInt(hex.substring(0, 2), 16)
    const g = parseInt(hex.substring(2, 4), 16)
    const b = parseInt(hex.substring(4, 6), 16)
    color = `rgba(${r}, ${g}, ${b}, ${opacityValue})`
  }
  return color
}

export const getMasteryTitleByValue = (value: number, masterySchema: MasterySchemaWithConfig): string => {
  const masteryLevels = masterySchema.config?.levels || []
  const masteryLevel = masteryLevels.find(ml => ml.minValue <= value && ml.maxValue >= value)
  return masteryLevel ? masteryLevel.title : 'tittel manlger'
}

export function useMasteryCalculations(masterySchema: MasterySchemaWithConfig | null) {
  const masteryLevels = masterySchema?.config?.levels || []
  const hasLevels = masteryLevels.length > 0

  const minValue = hasLevels
    ? Math.min(...masteryLevels.map((lev: MasteryConfigLevel) => lev.minValue))
    : 0
  const maxValue = hasLevels
    ? Math.max(...masteryLevels.map((lev: MasteryConfigLevel) => lev.maxValue))
    : 100
  const sliderValueIncrement = masterySchema?.config?.inputIncrement || 1
  const defaultValue = Math.floor((minValue + maxValue) / 2)
  const deltaValue = maxValue - minValue
  const flatTrendThreshold = masterySchema?.config?.flatTrendThreshold || 1

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
    deltaValue,
    sliderValueIncrement,
    defaultValue,
    calculateSafeMasteryValue,
    flatTrendThreshold,
    hasLevels,
  }
}
