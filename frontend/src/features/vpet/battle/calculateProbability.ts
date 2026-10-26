import type { BattleProbabilityConfig } from '../data/types'

export interface ProbabilityFighter {
  kind?: 'Digimon' | 'Appmon'
  level: string
  attribute: string
  hasXAntibody: boolean
}

function normalized(value: string, aliases: Record<string, string>, fallback: string) {
  const raw = value.trim()
  const match = Object.entries(aliases).find(([key]) => key.toLocaleLowerCase() === raw.toLocaleLowerCase())
  return match?.[1] ?? (raw || fallback)
}

function normalizedLevel(fighter: ProbabilityFighter, config: BattleProbabilityConfig) {
  const rawLevel = fighter.level.trim()
  if (fighter.kind === 'Appmon') return normalized(rawLevel, config.appmonLevelAliases, 'Sin dato')
  return normalized(rawLevel, config.levelAliases, 'Sin dato')
}

export function calculateProbability(
  attacker: ProbabilityFighter,
  defender: ProbabilityFighter,
  config: BattleProbabilityConfig,
) {
  const attackerLevel = normalizedLevel(attacker, config)
  const defenderLevel = normalizedLevel(defender, config)
  const attackerRank = config.levelRanks[attackerLevel]
  const defenderRank = config.levelRanks[defenderLevel]
  const difference = attackerRank !== undefined && defenderRank !== undefined ? attackerRank - defenderRank : 0
  const magnitude = config.levelDifferenceModifiers[String(Math.abs(difference))]
    ?? Math.abs(difference) * config.levelStep
  let levelProbability = config.baseProbability + (difference >= 0 ? magnitude : -magnitude)
  const nonCombatants = new Set(config.nonCombatantLevels)
  const attackerBaby = nonCombatants.has(attackerLevel)
  const defenderBaby = nonCombatants.has(defenderLevel)
  const mixedBabyBattle = attackerBaby !== defenderBaby
  if (mixedBabyBattle) levelProbability = attackerBaby
    ? config.nonCombatantWinProbability
    : 1 - config.nonCombatantWinProbability

  const neutral = new Set(config.neutralAttributes.map(value => value.toLocaleLowerCase()))
  const attackerAttribute = normalized(attacker.attribute, config.attributeAliases, 'Sin dato')
  const defenderAttribute = normalized(defender.attribute, config.attributeAliases, 'Sin dato')
  let attributeModifier = 0
  if (!mixedBabyBattle && !neutral.has(attackerAttribute.toLocaleLowerCase()) && !neutral.has(defenderAttribute.toLocaleLowerCase())) {
    if (config.attributeAdvantages[attackerAttribute] === defenderAttribute) attributeModifier = config.attributeAdvantage
    if (config.attributeAdvantages[defenderAttribute] === attackerAttribute) attributeModifier = -config.attributeAdvantage
  }
  const xAntibodyModifier = mixedBabyBattle || attacker.hasXAntibody === defender.hasXAntibody
    ? 0
    : attacker.hasXAntibody ? config.xAntibodyBonus : -config.xAntibodyBonus
  const attackerWinProbability = Math.max(
    config.minimumProbability,
    Math.min(config.maximumProbability, levelProbability + attributeModifier + xAntibodyModifier),
  )
  return {
    attackerWinProbability,
    defenderWinProbability: 1 - attackerWinProbability,
    levelProbability,
    attributeModifier,
    xAntibodyModifier,
  }
}
