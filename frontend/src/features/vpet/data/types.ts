export interface VPetDataCounts {
  referenceRecords: number
  referenceImages: number
  availableImages: number
  catalogFamilies: number
  protocolProfiles: number
}

export interface BattleProbabilityConfig {
  baseProbability: number
  levelStep: number
  levelDifferenceModifiers: Record<string, number>
  attributeAdvantage: number
  xAntibodyBonus: number
  minimumProbability: number
  maximumProbability: number
  nonCombatantLevels: string[]
  nonCombatantWinProbability: number
  levelRanks: Record<string, number>
  levelAliases: Record<string, string>
  appmonLevelAliases: Record<string, string>
  attributeAliases: Record<string, string>
  neutralAttributes: string[]
  attributeAdvantages: Record<string, string>
  noise: { enabled: boolean; amplitude: number }
}

export interface ProtocolProfile {
  name: string
  wireCode: string
  packetCount: number
  digitsPerPacket: number
  alpha: null | { command: string; protocolRepresentative: string }
}

export interface VPetBootstrap {
  schemaVersion: number
  dataVersion: string
  counts: VPetDataCounts
  probability: BattleProbabilityConfig
  protocols: {
    schemaVersion: number
    profiles: Record<string, ProtocolProfile>
    verifiedResults: Record<string, Record<string, string>>
    dmcProxyModels: string[]
  }
  resources: Record<string, string>
}

export interface ReferenceProfile {
  id: string
  normalizedName: string
  variantIndex: number
  selectorLabel: string
  name: string
  kind: 'Digimon' | 'Appmon'
  level: string | null
  type: string | null
  attribute: string | null
  attacks: string[]
  description: string
  antibody: boolean
  appmon_id: string | number | null
  image: string | null
  source_url: string | null
}

export interface ReferenceSearchResult {
  total: number
  offset: number
  limit: number
  items: ReferenceProfile[]
  source: 'atlas' | 'json-fallback'
}

export interface CatalogEntry {
  nombre: string
  identificador: number | null
  version: string
  version_comunicacion?: string
  evidencia: string
}

export interface CatalogFamily {
  schema: number
  family: string
  nombre?: string
  entradas: CatalogEntry[]
  referenceProfiles?: Record<string, ReferenceProfile>
}
