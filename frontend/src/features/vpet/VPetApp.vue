<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { calculateProbability } from './battle/calculateProbability'
import { loadCatalogFamily, loadReferenceVariants, loadVPetBootstrap, loadVPetConfig, referenceImageUrl, searchReferenceBook } from './data/client'
import type { CatalogEntry, ReferenceProfile, ReferenceSearchResult, VPetBootstrap } from './data/types'
import { Ch340Transport } from './usb/ch340'

type Tab = 'battle' | 'probability' | 'system'
type ModelStatus = 'verified' | 'testing' | 'untested'

const levelDisplayOrder = ['In-Training I', 'In-Training II', 'Rookie', 'Champion', 'Armor', 'Hybrid', 'Ultimate', 'Mega']
const classicAlphaModels = new Set(['pen20', 'penx', 'accel', 'mini', 'xrosmini', 'dcomplete', 'dmx', 'penz', 'dmc'])
const catalogBackedModels = new Set(['pen20', 'penx', 'accel', 'mini', 'dmx', 'penz', 'dmc'])

interface DmcProxy { id: string; name: string; level: string; attribute: string; battle_eligible: boolean; version_word: number; slot_word: number; base_power: number | null; attribute_word: number }

const modelStatuses: Record<string, ModelStatus> = {
  dcomplete: 'verified', dmc: 'verified', dmx: 'verified', mini: 'verified',
  pen20: 'verified', penx: 'verified', xrosmini: 'verified',
  accel: 'testing', penc: 'testing',
  dm20: 'untested', dmgz: 'untested', dmh: 'untested', dmog: 'untested',
  dmxw: 'untested', pengz: 'untested', penog: 'untested', penz: 'untested',
}

const modelNames: Record<string, string> = {
  accel: 'Digimon Accel', dcomplete: 'Digivice Ver. Complete', dm20: 'Digital Monster Ver.20th',
  dmc: 'Digital Monster Color', dmgz: 'Digital Monster Color Godzilla',
  dmh: 'Digital Monster Color Monster Hunter', dmog: 'Digital Monster original',
  dmx: 'Digital Monster X', dmxw: 'Digital Monster Color Xros Wars', mini: 'Digimon Mini',
  pen20: 'Pendulum Ver.20th', penc: 'Pendulum Color', pengz: 'Pendulum Color Godzilla',
  penog: 'Pendulum original', penx: 'Pendulum X', penz: 'Pendulum Z',
  xrosmini: 'Digimon Xros Wars Mini',
}

const statusLabels: Record<ModelStatus, string> = {
  verified: '✅', testing: '🧪', untested: '❌',
}

const activeTab = ref<Tab>('battle')
const bootstrap = ref<VPetBootstrap | null>(null)
const query = ref('')
const searchResult = ref<ReferenceSearchResult | null>(null)
const selectedWeb = ref<ReferenceProfile | null>(null)
const selectedModel = ref('penx')
const loading = ref(true)
const searching = ref(false)
const error = ref('')
const imageFailed = ref(false)
const physicalImageFailed = ref(false)
const physicalVPet = ref<ReferenceProfile | null>(null)
const battleState = ref<'idle' | 'preparing' | 'armed' | 'fighting' | 'complete' | 'error'>('idle')
const battleWinner = ref<'web' | 'vpet' | null>(null)
const battleProbability = ref<number | null>(null)
const battleConnectionError = ref('')
const consoleLines = ref<string[]>(['SISTEMA: inicializando Digimon Alpha…'])
const gpsState = ref<'idle' | 'loading' | 'active' | 'error'>('idle')
const latitude = ref<number | null>(null)
const longitude = ref<number | null>(null)
const gpsAccuracy = ref<number | null>(null)
const usbState = ref<'unsupported' | 'disconnected' | 'connecting' | 'connected'>(Ch340Transport.supported() ? 'disconnected' : 'unsupported')
const usbLabel = ref('')
let searchTimer: ReturnType<typeof setTimeout> | undefined
let gpsWatchId: number | undefined
let usbTransport: Ch340Transport | undefined
let serialText = ''
const serialDecoder = new TextDecoder()
let activeCatalog: CatalogEntry[] = []
let physicalProfiles = new Map<string, ReferenceProfile>()
let activeDmcProxy: DmcProxy | null = null
let dmcExchangeProcessed = false
let firmwareLineChain: Promise<void> = Promise.resolve()
let battleDeadline = 0
let battleRetryTimer: ReturnType<typeof setTimeout> | undefined

const calculatorAttacker = ref({ level: 'Mega', attribute: 'Vaccine', hasXAntibody: false })
const calculatorDefender = ref({ level: 'Rookie', attribute: 'Data', hasXAntibody: false })
const levelOptions = computed(() => {
  const available = Object.keys(bootstrap.value?.probability.levelRanks ?? {})
  return [...levelDisplayOrder.filter(level => available.includes(level)), ...available.filter(level => !levelDisplayOrder.includes(level))]
})
const attributeOptions = ['Vaccine', 'Virus', 'Data', 'Free', 'Variable', 'Unknown']
const modelOptions = computed(() => Object.entries(bootstrap.value?.protocols.profiles ?? {}))
const selectedModelName = computed(() => modelNames[selectedModel.value] ?? 'V-Pet físico')
const selectedImage = computed(() => imageFailed.value ? '' : referenceImageUrl(selectedWeb.value))
const physicalImage = computed(() => physicalImageFailed.value ? '' : referenceImageUrl(physicalVPet.value))
const selectedAlphaSupported = computed(() => classicAlphaModels.has(selectedModel.value) && Boolean(bootstrap.value?.protocols.profiles[selectedModel.value]?.alpha))
const selectedWebBattleLevel = computed(() => {
  if (!selectedWeb.value || !bootstrap.value) return 'Sin dato'
  const aliases = selectedWeb.value.kind === 'Appmon' ? bootstrap.value.probability.appmonLevelAliases : bootstrap.value.probability.levelAliases
  const raw = selectedWeb.value.level?.trim() || 'Sin dato'
  return Object.entries(aliases).find(([key]) => key.toLocaleLowerCase() === raw.toLocaleLowerCase())?.[1] ?? raw
})
const selectedWebIsBaby = computed(() => bootstrap.value?.probability.nonCombatantLevels.includes(selectedWebBattleLevel.value) ?? false)
const canPrepareBattle = computed(() => usbState.value === 'connected' && Boolean(selectedWeb.value) && !selectedWebIsBaby.value && selectedAlphaSupported.value && battleState.value !== 'preparing' && battleState.value !== 'armed' && battleState.value !== 'fighting')
const probability = computed(() => {
  if (!bootstrap.value) return null
  return calculateProbability(calculatorAttacker.value, calculatorDefender.value, bootstrap.value.probability)
})
const attackerPercent = computed(() => Math.round((probability.value?.attackerWinProbability ?? .5) * 100))
const levelMatrix = computed(() => {
  const config = bootstrap.value?.probability
  if (!config) return { headers: [] as string[], rows: [] as { name: string; values: number[] }[] }
  const levels = levelOptions.value.map(level => [level, config.levelRanks[level]] as const)
  const nonCombatants = new Set(config.nonCombatantLevels)
  const clamp = (value: number) => Math.max(config.minimumProbability, Math.min(config.maximumProbability, value))
  return {
    headers: levels.map(([name]) => name),
    rows: levels.map(([attacker, attackerRank]) => ({
      name: attacker,
      values: levels.map(([defender, defenderRank]) => {
        const difference = attackerRank - defenderRank
        const magnitude = config.levelDifferenceModifiers[String(Math.abs(difference))] ?? Math.abs(difference) * config.levelStep
        if (nonCombatants.has(attacker) !== nonCombatants.has(defender)) {
          return nonCombatants.has(attacker) ? config.nonCombatantWinProbability : 1 - config.nonCombatantWinProbability
        }
        return clamp(config.baseProbability + (difference >= 0 ? magnitude : -magnitude))
      }),
    })),
  }
})
const attributeMatrix = computed(() => {
  const config = bootstrap.value?.probability
  const headers = ['Vaccine', 'Virus', 'Data', 'Free']
  if (!config) return { headers, rows: [] as { name: string; values: number[] }[] }
  const neutral = new Set(config.neutralAttributes.map(value => value.toLocaleLowerCase()))
  return {
    headers,
    rows: headers.map(attacker => ({ name: attacker, values: headers.map(defender => {
      if (neutral.has(attacker.toLocaleLowerCase()) || neutral.has(defender.toLocaleLowerCase())) return 0
      if (config.attributeAdvantages[attacker] === defender) return config.attributeAdvantage
      if (config.attributeAdvantages[defender] === attacker) return -config.attributeAdvantage
      return 0
    }) })),
  }
})

function matrixClass(value: number, neutral: number) {
  return value > neutral ? 'matrix-good' : value < neutral ? 'matrix-bad' : ''
}

function formatModifier(value: number) {
  const percent = Math.round(value * 100)
  return `${percent > 0 ? '+' : ''}${percent}%`
}

function log(message: string) {
  const time = new Date().toLocaleTimeString('es-MX', { hour12: false })
  consoleLines.value = [...consoleLines.value.slice(-39), `${time}  ${message}`]
}

function receiveUsbData(data: Uint8Array) {
  serialText += serialDecoder.decode(data, { stream: true })
  if (selectedModel.value === 'dmc' && !dmcExchangeProcessed && /r:[0-9A-F]{32}[\s\S]*r:[0-9A-F]{32}/i.test(serialText)) {
    dmcExchangeProcessed = processDmcExchange(serialText)
  }
  const lines = serialText.split(/\r?\n/)
  serialText = lines.pop() ?? ''
  for (const line of lines) if (line.trim()) {
    const clean = line.trim()
    log(`SERIAL: ${clean}`)
    firmwareLineChain = firmwareLineChain.then(() => processFirmwareLine(clean)).catch(cause => {
      battleState.value = 'error'
      log(`BATALLA ERROR: ${cause instanceof Error ? cause.message : String(cause)}`)
    })
  }
}

function transport() {
  usbTransport ??= new Ch340Transport(receiveUsbData, connected => {
    if (!connected && ['preparing', 'armed', 'fighting'].includes(battleState.value)) {
      battleState.value = 'error'
      battleConnectionError.value = 'Se desconectó el Beta Link durante la batalla.'
    }
    usbState.value = connected ? 'connected' : 'disconnected'
    if (!connected) usbLabel.value = ''
  })
  return usbTransport
}

async function toggleUsb() {
  if (usbState.value === 'connecting') return
  if (usbState.value === 'connected') {
    await transport().disconnect()
    log('USB: Beta Link desconectado.')
    return
  }
  usbState.value = 'connecting'
  try {
    const info = await transport().connect()
    usbLabel.value = info.label
    usbState.value = 'connected'
    log(`USB: ${info.label} conectado a 9600 baudios.`)
    log('USB: listo para recibir mensajes del firmware.')
  } catch (cause) {
    usbState.value = Ch340Transport.supported() ? 'disconnected' : 'unsupported'
    const message = cause instanceof Error ? cause.message : 'No se pudo conectar el Beta Link.'
    log(`USB ERROR: ${message}`)
  }
}

async function prepareBattle() {
  if (!canPrepareBattle.value || !selectedWeb.value || !bootstrap.value) return
  battleState.value = 'preparing'
  battleConnectionError.value = ''
  battleWinner.value = null
  battleProbability.value = null
  dmcExchangeProcessed = false
  physicalVPet.value = null
  physicalImageFailed.value = false
  try {
    activeCatalog = []
    physicalProfiles.clear()
    activeDmcProxy = null
    if (catalogBackedModels.has(selectedModel.value)) {
      const catalog = await loadCatalogFamily(selectedModel.value, true)
      activeCatalog = catalog.entradas.filter(entry => entry.identificador !== null)
      physicalProfiles = new Map(Object.entries(catalog.referenceProfiles ?? {}))
    }
    if (selectedModel.value === 'dmc') {
      const config = await loadVPetConfig<{ profiles: DmcProxy[] }>('dmc-battle-profiles')
      activeDmcProxy = chooseDmcProxy(config.profiles, selectedWeb.value)
      log(`MÁSCARA DMC: ${activeDmcProxy.name} (${activeDmcProxy.level}, ${activeDmcProxy.attribute}).`)
    }
    if (selectedModel.value === 'xrosmini') {
      for (const name of ['Shoutmon', 'Greymon (2010 Anime Version)', 'Guilmon', 'Agumon', 'V-Mon', 'Shoutmon X4']) {
        try {
          const variants = await loadReferenceVariants(name)
          if (variants[0]) physicalProfiles.set(name, variants[0])
        } catch { /* An undocumented variant remains generic. */ }
      }
    }
    battleDeadline = Date.now() + 100_000
    await armSelectedModel()
    battleState.value = 'armed'
    log(`BATALLA: ${selectedModelName.value} armado durante 100 segundos. Inicia la batalla y mantén unidos los tres pines.`)
  } catch (cause) {
    battleState.value = 'error'
    battleConnectionError.value = cause instanceof Error ? cause.message : 'No se pudo preparar la batalla.'
    log(`BATALLA ERROR: ${battleConnectionError.value}`)
  }
}

function chooseDmcProxy(profiles: DmcProxy[], fighter: ReferenceProfile) {
  const aliases: Record<string, string> = {
    rookie: 'Rookie', child: 'Rookie', champion: 'Champion', adult: 'Champion', armor: 'Champion', hybrid: 'Champion', standard: 'Champion',
    ultimate: 'Ultimate', perfect: 'Ultimate', mega: 'Mega', super: 'Mega', god: 'Mega', unknown: 'Champion', '－': 'Champion',
  }
  const rawLevel = (fighter.level || 'Unknown').replace('(Xros Wars)', '').trim()
  const wantedLevel = aliases[rawLevel.toLocaleLowerCase()] ?? rawLevel
  const eligible = profiles.filter(profile => profile.battle_eligible && profile.base_power !== null && profile.level === wantedLevel)
  const exact = eligible.filter(profile => profile.attribute.toLocaleLowerCase() === (fighter.attribute || '').toLocaleLowerCase())
  const candidates = (exact.length ? exact : eligible).sort((a, b) => a.id.localeCompare(b.id))
  if (!candidates.length) throw new Error(`No existe una máscara DMC combatible para el nivel ${fighter.level || 'desconocido'}.`)
  let hash = 0
  for (const character of fighter.name.toLocaleLowerCase()) hash = ((hash * 31) + character.charCodeAt(0)) >>> 0
  return candidates[hash % candidates.length]
}

async function armSelectedModel() {
  const command = bootstrap.value?.protocols.profiles[selectedModel.value]?.alpha?.command
  if (!command) throw new Error('Este modelo no tiene un comando Alpha disponible.')
  if (selectedModel.value === 'dmc') {
    if (!activeDmcProxy || activeDmcProxy.base_power === null) throw new Error('La máscara DMC no está preparada.')
    const word = (value: number) => value.toString(16).toUpperCase().padStart(4, '0')
    await transport().write(`${command}:${word(activeDmcProxy.version_word)}:${word(activeDmcProxy.slot_word)}:${word(activeDmcProxy.base_power)}:${word(activeDmcProxy.attribute_word)}\n`)
    return
  }
  await transport().write(`${command}\n`)
}

function scheduleBattleRetry() {
  if (battleRetryTimer) clearTimeout(battleRetryTimer)
  if (Date.now() >= battleDeadline) {
    battleState.value = 'error'
    battleConnectionError.value = 'Se superó el tiempo de espera de 100 segundos sin detectar al V-Pet.'
    log(`BATALLA ERROR: ${battleConnectionError.value}`)
    return
  }
  battleRetryTimer = setTimeout(() => {
    if (battleState.value !== 'armed') return
    void armSelectedModel().catch(cause => {
      battleState.value = 'error'
      battleConnectionError.value = cause instanceof Error ? cause.message : String(cause)
      log(`BATALLA ERROR: ${battleConnectionError.value}`)
    })
  }, 250)
}

function genericPhysicalProfile(name: string, level: string | null = null, attribute: string | null = null, antibody = false): ReferenceProfile {
  return { id: `physical-${selectedModel.value}`, normalizedName: name.toLocaleLowerCase().replace(/[^a-z0-9]+/g, ''), variantIndex: 0, selectorLabel: name, name, kind: 'Digimon', level, type: antibody ? 'X-Antibody' : null, attribute, attacks: [], description: '', antibody, appmon_id: null, image: null, source_url: null }
}

function catalogIdentity(identifier: number, versions: string[]) {
  const matches = activeCatalog.filter(entry => entry.identificador === identifier && (entry.version === 'comun' || versions.includes(entry.version) || Boolean(entry.version_comunicacion && versions.includes(entry.version_comunicacion))))
  const names = [...new Set(matches.map(entry => entry.nombre))]
  if (names.length !== 1) return null
  return { name: names[0], profile: physicalProfiles.get(names[0]) ?? genericPhysicalProfile(names[0]) }
}

function identifyBattleQuery(packet: string) {
  const model = selectedModel.value
  const words = packet.split('-').map(value => Number.parseInt(value, 16))
  if (model === 'penx' || model === 'mini' || model === 'accel') {
    if (!/^[0-9A-F]{4}$/.test(packet) || (words[0] & 0xf) !== 9) return null
    if (model === 'accel') return { name: 'Digimon Accel', profile: genericPhysicalProfile('Digimon Accel') }
    return catalogIdentity((words[0] >> 4) & 0xff, [String((words[0] >> 12) & 0xf)])
  }
  if (model === 'xrosmini') {
    if (!/^[0-9A-F]{4}$/.test(packet) || (words[0] & 0xf) !== 7) return null
    const key = `${(words[0] >> 12) & 0xf}:${(words[0] >> 4) & 0xff}`
    const names: Record<string, string> = { '1:1': 'Shoutmon', '1:11': 'Guilmon', '1:12': 'Agumon', '1:13': 'V-Mon', '1:16': 'Shoutmon X4', '2:1': 'Greymon (2010 Anime Version)' }
    const name = names[key]
    return name ? { name, profile: physicalProfiles.get(name) ?? genericPhysicalProfile(name) } : null
  }
  if (model === 'dcomplete') return /^[0-9A-F]{4}$/.test(packet) ? { name: 'Digivice Ver. Complete', profile: genericPhysicalProfile('Digivice Ver. Complete') } : null
  if ((model === 'dmx' || model === 'penz') && words.length === 2 && words.every(word => (word & 0xf) === 0xe)) {
    const versionCode = (words[0] >> 4) & 0xf
    const namespace = model === 'dmx' ? ['XA', 'XB', 'XC', 'XD', 'XE', 'XF'][versionCode] : versionCode < 9 ? 'Z1' : 'Z2'
    const stage = ['In-Training II', 'Rookie', 'Champion', 'Ultimate', 'Mega', 'Mega'][(words[1] >> 13) & 7] ?? 'Unknown'
    const attribute = ['Vaccine', 'Data', 'Virus', 'Free'][(words[1] >> 4) & 3]
    const identified = catalogIdentity((words[1] >> 6) & 0x7f, namespace ? [namespace] : [])
    return identified ?? { name: model === 'dmx' ? 'Digital Monster X' : 'Pendulum Z', profile: genericPhysicalProfile(model === 'dmx' ? 'Digital Monster X' : 'Pendulum Z', stage, attribute, model === 'dmx') }
  }
  if (model === 'pen20' && words.length === 2 && words.every(word => (word & 0xf) === 0xe)) return catalogIdentity((words[1] >> 6) & 0xff, ['comun'])
  return null
}

async function processFirmwareLine(line: string) {
  if (/bit .*timed out|too short|incomplet|interrump|rechaz/i.test(line)) {
    battleState.value = 'error'
    battleConnectionError.value = 'La conexión con el V-Pet fue incompleta o se interrumpió. Separa los pines y vuelve a preparar la batalla.'
    log(`BATALLA ERROR: ${battleConnectionError.value}`)
    return
  }
  if (selectedModel.value === 'dmc' && !dmcExchangeProcessed && /(?:^|\s)r:[0-9A-F]{32}(?=\s|$)/i.test(line)) dmcExchangeProcessed = processDmcExchange(line)
  if (/^alpha:armed:family-battle-v\d+:[0-4CM]$/.test(line)) {
    battleState.value = 'armed'
    log('BATALLA: listo para la batalla.')
    return
  }
  const queryMatch = line.match(/^alpha:q:([0-9A-F-]+)$/i)
  if (queryMatch && battleState.value === 'armed') {
    battleState.value = 'fighting'
    const identity = identifyBattleQuery(queryMatch[1].toUpperCase())
    if (!identity?.profile || !selectedWeb.value || !bootstrap.value) {
      await transport().write('P\n')
      battleState.value = 'error'
      battleConnectionError.value = `La lectura ${queryMatch[1]} no identifica este V-Pet de forma única.`
      log(`BATALLA ERROR: ${battleConnectionError.value} Se concede la victoria al V-Pet.`)
      return
    }
    physicalVPet.value = identity.profile
    const result = calculateProbability({
      kind: selectedWeb.value.kind,
      level: selectedWeb.value.level || 'Unknown',
      attribute: selectedWeb.value.attribute || 'Unknown',
      hasXAntibody: selectedWeb.value.antibody,
    }, {
      kind: identity.profile.kind,
      level: identity.profile.level || 'Unknown',
      attribute: identity.profile.attribute || 'Unknown',
      hasXAntibody: identity.profile.antibody,
    }, bootstrap.value.probability)
    const amplitude = bootstrap.value.probability.noise.enabled ? bootstrap.value.probability.noise.amplitude : 0
    const effective = Math.max(bootstrap.value.probability.minimumProbability, Math.min(bootstrap.value.probability.maximumProbability, result.attackerWinProbability + (Math.random() * 2 - 1) * amplitude))
    const webWins = Math.random() < effective
    battleProbability.value = effective
    battleWinner.value = webWins ? 'web' : 'vpet'
    await transport().write(webWins ? 'W\n' : 'P\n')
    log(`V-PET: ${identity.name}. Probabilidad rival web: ${(effective * 100).toFixed(1)}%.`)
    log(`BATALLA: decisión enviada (${webWins ? 'rival web' : 'V-Pet'}).`)
    return
  }
  if (line === 'alpha:decision:web') battleWinner.value = 'web'
  if (line === 'alpha:decision:vpet' || line === 'alpha:decision:timeout-vpet') battleWinner.value = 'vpet'
  if (line === 'alpha:done:default-mode') {
    if (battleState.value === 'armed') {
      scheduleBattleRetry()
      return
    }
    if (battleState.value === 'fighting' || battleState.value === 'error') {
      battleState.value = battleWinner.value ? 'complete' : 'error'
      if (battleWinner.value) log(`GANADOR: ${battleWinner.value === 'web' ? selectedWeb.value?.name : physicalVPet.value?.name}.`)
      else if (!battleConnectionError.value) battleConnectionError.value = 'La conexión terminó sin un resultado completo del V-Pet.'
    }
  }
}

function processDmcExchange(line: string) {
  const received = [...line.matchAll(/(?:^|\s)r:([0-9A-F]{32})(?=\s|$)/gi)].map(match => match[1].toUpperCase())
  if (received.length < 2) return false
  const words = (block: string) => Array.from({ length: 8 }, (_, index) => Number.parseInt(block.slice(index * 4, index * 4 + 4), 16))
  const identityWords = words(received[0])
  const resultWords = words(received[1])
  if (identityWords[0] !== 0x4744 || identityWords[1] !== 0x4c43 || (identityWords.slice(0, 7).reduce((sum, word) => sum + word, 0) & 0xffff) !== identityWords[7]) return false
  const version = String(identityWords[3] + 1).padStart(2, '0')
  const identity = catalogIdentity(identityWords[4], [version])
  if (identity) {
    physicalVPet.value = identity.profile
    physicalImageFailed.value = false
    log(`V-PET DMC: ${identity.name}.`)
    if (!identity.profile.image) {
      void loadReferenceVariants(identity.name).then(variants => {
        if (variants[0]) {
          physicalProfiles.set(identity.name, variants[0])
          physicalVPet.value = variants[0]
          physicalImageFailed.value = false
        }
      }).catch(() => log(`REFERENCE BOOK: no se encontraron datos para ${identity.name}.`))
    }
  }
  if (resultWords[0] === 0x4744 && resultWords[1] === 0x4c43 && resultWords[2] === 0x0002 && (resultWords.slice(0, 7).reduce((sum, word) => sum + word, 0) & 0xffff) === resultWords[7]) {
    battleWinner.value = (resultWords[4] & 1) !== 0 ? 'vpet' : 'web'
    battleState.value = 'fighting'
    log(`RESULTADO DMC: ${battleWinner.value === 'vpet' ? 'ganó el V-Pet físico' : 'ganó el rival web'}.`)
  }
  return true
}

function modelOptionLabel(key: string) {
  const status = modelStatuses[key] ?? 'untested'
  return `${modelNames[key] ?? key} (${statusLabels[status]})`
}

async function runSearch(selectFirst = false) {
  searching.value = true
  try {
    searchResult.value = await searchReferenceBook(query.value, 0, 24)
    if (selectFirst && searchResult.value.items.length) selectFighter(searchResult.value.items[0])
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'No se pudo consultar el Reference Book.'
    log(`ERROR: ${error.value}`)
  } finally {
    searching.value = false
  }
}

function selectFighter(profile: ReferenceProfile) {
  selectedWeb.value = profile
  query.value = profile.name
  imageFailed.value = false
  calculatorAttacker.value = {
    level: profile.level || 'Unknown',
    attribute: profile.attribute || 'Unknown',
    hasXAntibody: profile.antibody,
  }
  log(`RIVAL WEB: ${profile.name}`)
}

function clearAll() {
  if (battleRetryTimer) clearTimeout(battleRetryTimer)
  battleRetryTimer = undefined
  battleDeadline = 0
  void usbTransport?.disconnect()
  selectedWeb.value = null
  query.value = ''
  searchResult.value = null
  selectedModel.value = 'penx'
  imageFailed.value = false
  physicalImageFailed.value = false
  physicalVPet.value = null
  battleState.value = 'idle'
  battleWinner.value = null
  battleProbability.value = null
  battleConnectionError.value = ''
  dmcExchangeProcessed = false
  activeCatalog = []
  physicalProfiles.clear()
  activeDmcProxy = null
  stopGps()
  consoleLines.value = ['SISTEMA: interfaz reiniciada.', 'SISTEMA: lista para una nueva sesión.']
  serialText = ''
}

function startGps() {
  if (!navigator.geolocation) {
    gpsState.value = 'error'
    log('GPS: navegador no compatible.')
    return
  }
  gpsState.value = 'loading'
  gpsWatchId = navigator.geolocation.watchPosition(
    position => {
      latitude.value = position.coords.latitude
      longitude.value = position.coords.longitude
      gpsAccuracy.value = position.coords.accuracy
      gpsState.value = 'active'
    },
    locationError => {
      gpsState.value = 'error'
      log(`GPS: ${locationError.message}`)
    },
    { enableHighAccuracy: true, maximumAge: 1000, timeout: 15000 },
  )
}

function stopGps() {
  if (gpsWatchId !== undefined) navigator.geolocation.clearWatch(gpsWatchId)
  gpsWatchId = undefined
  gpsState.value = 'idle'
  latitude.value = null
  longitude.value = null
  gpsAccuracy.value = null
}

watch(query, () => {
  if (searchTimer) clearTimeout(searchTimer)
  if (selectedWeb.value?.name === query.value) return
  searchTimer = setTimeout(() => runSearch(), 280)
})

watch(selectedModel, value => log(`MODELO: ${bootstrap.value?.protocols.profiles[value]?.name ?? value}`))

async function initialize() {
  loading.value = true
  error.value = ''
  try {
    bootstrap.value = await loadVPetBootstrap()
    log(`DATOS: versión ${bootstrap.value.dataVersion}`)
    log(`REFERENCE BOOK: ${bootstrap.value.counts.referenceRecords} perfiles disponibles.`)
    searchResult.value = { total: 0, offset: 0, limit: 24, items: [], source: 'atlas' }
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'No se pudo iniciar Digimon Alpha.'
    log(`ERROR: ${error.value}`)
  } finally {
    loading.value = false
  }
}

onMounted(initialize)

onBeforeUnmount(() => {
  if (searchTimer) clearTimeout(searchTimer)
  if (battleRetryTimer) clearTimeout(battleRetryTimer)
  stopGps()
  void usbTransport?.disconnect()
})
</script>

<template>
  <div class="alpha-app">
    <header class="alpha-header">
      <a class="alpha-brand" href="/">
        <span class="alpha-mark" aria-hidden="true"><i /><i /><i /><i /></span>
        <span><b>DIGIMON ALPHA</b><small>V-PET LINK SYSTEM</small></span>
      </a>
      <div class="header-status">
        <span :class="{ online: bootstrap }"><i />{{ bootstrap ? 'DATOS EN LÍNEA' : 'SIN CONEXIÓN' }}</span>
        <span class="beta-link-status" :class="{ online: usbState === 'connected' }"><i />{{ usbState === 'connected' ? 'BETA LINK EN LÍNEA' : usbState === 'connecting' ? 'CONECTANDO BETA LINK' : 'BETA LINK DESCONECTADO' }}</span>
        <a href="/#proyectos">PORTAFOLIO ↗</a>
      </div>
    </header>

    <nav class="alpha-tabs" aria-label="Secciones V-Pet">
      <button :class="{ active: activeTab === 'battle' }" @click="activeTab = 'battle'"><small>01</small> BATALLA</button>
      <button :class="{ active: activeTab === 'probability' }" @click="activeTab = 'probability'"><small>02</small> PROBABILIDAD</button>
      <button :class="{ active: activeTab === 'system' }" @click="activeTab = 'system'"><small>03</small> SISTEMA</button>
      <button class="clear-button" @click="clearAll">LIMPIAR TODO</button>
    </nav>

    <main>
      <div v-if="error" class="connection-banner">
        <span><b>API SIN CONEXIÓN</b>{{ error }}</span>
        <button @click="initialize">REINTENTAR</button>
      </div>
      <div v-if="loading" class="loading-screen"><i /><i /><i /><span>CARGANDO REFERENCE BOOK</span></div>

      <section v-else-if="activeTab === 'battle'" class="battle-view">
        <div class="setup-bar panel">
          <label>
            <span>RIVAL WEB</span>
            <input v-model="query" autocomplete="off" placeholder="Buscar Digimon o Appmon">
            <small>{{ searching ? 'BUSCANDO…' : `${searchResult?.total ?? 0} RESULTADOS · ${(searchResult?.source ?? '—').toUpperCase()}` }}</small>
          </label>
          <label>
            <span>MODELO V-PET</span>
            <select v-model="selectedModel">
              <option v-for="([key]) in modelOptions" :key="key" :value="key">{{ modelOptionLabel(key) }}</option>
            </select>
            <small>EL DIGIMON FÍSICO SE DETECTARÁ AUTOMÁTICAMENTE</small>
          </label>
          <div class="battle-actions">
            <button class="usb-button" :class="{ connected: usbState === 'connected' }" :disabled="usbState === 'unsupported' || usbState === 'connecting'" @click="toggleUsb"><span>USB</span> {{ usbState === 'connected' ? 'DESCONECTAR' : usbState === 'connecting' ? 'CONECTANDO…' : 'CONECTAR BETA LINK' }}<small>{{ usbState === 'unsupported' ? 'WEBUSB NO DISPONIBLE' : usbLabel || 'CH340 · 9600 BAUDIOS' }}</small></button>
            <button class="prepare-battle-button" :disabled="!canPrepareBattle" @click="prepareBattle">PREPARAR BATALLA<small>{{ !selectedAlphaSupported ? 'MODELO TODAVÍA NO DISPONIBLE' : !selectedWeb ? 'SELECCIONA UN RIVAL' : selectedWebIsBaby ? 'LOS BB NO PUEDEN PELEAR' : usbState !== 'connected' ? 'CONECTA EL BETA LINK' : 'UNA SOLA CONEXIÓN' }}</small></button>
          </div>
        </div>

        <div class="battle-instruction" :class="battleState">
          <template v-if="usbState !== 'connected'"><b>1</b><span>CONECTA EL BETA LINK</span><small>Usa el botón USB para abrir el puerto.</small></template>
          <template v-else-if="!selectedWeb"><b>2</b><span>SELECCIONA UN RIVAL WEB</span><small>Busca un Digimon o Appmon antes de preparar la pelea.</small></template>
          <template v-else-if="selectedWebIsBaby"><b>!</b><span>ESTE DIGIMON TODAVÍA ES BB</span><small>In-Training I, In-Training II y los Appmon de nivel － no pueden participar en batallas.</small></template>
          <template v-else-if="!selectedAlphaSupported"><b>!</b><span>MODELO TODAVÍA NO DISPONIBLE</span><small>Este protocolo requiere una máscara Color o todavía no tiene comando Alpha.</small></template>
          <template v-else-if="battleState === 'preparing'"><b>…</b><span>PREPARANDO BATALLA</span><small>Cargando el catálogo y armando el firmware.</small></template>
          <template v-else-if="battleState === 'armed'"><b>✓</b><span>LISTO: YA PUEDES CONECTAR EL V-PET</span><small>Inicia la batalla en {{ selectedModelName }} y mantén unidos los tres pines.</small></template>
          <template v-else-if="battleState === 'fighting'"><b>VS</b><span>BATALLA EN CURSO</span><small>No separes los pines hasta que termine el intercambio.</small></template>
          <template v-else-if="battleState === 'complete'"><b>✓</b><span>BATALLA FINALIZADA</span><small>Puedes preparar otra batalla.</small></template>
          <template v-else-if="battleState === 'error'"><b>!</b><span>LA BATALLA NO TERMINÓ</span><small>Revisa la consola y vuelve a preparar la pelea.</small></template>
          <template v-else><b>3</b><span>PULSA PREPARAR BATALLA</span><small>Todavía no conectes los tres pines del V-Pet.</small></template>
        </div>
        <div v-if="battleConnectionError" class="battle-connection-error" role="alert"><b>ERROR DE CONEXIÓN</b><span>{{ battleConnectionError }}</span></div>

        <div v-if="query && selectedWeb?.name !== query" class="search-results panel">
          <button v-for="profile in searchResult?.items" :key="profile.id" @click="selectFighter(profile)">
            <span>{{ profile.name }}</span><small>{{ profile.level || 'Sin nivel' }} · {{ profile.attribute || 'Sin atributo' }}</small>
          </button>
          <p v-if="!searching && !searchResult?.items.length">SIN COINCIDENCIAS</p>
        </div>

        <div class="arena">
          <article class="fighter-card web-fighter" :class="{ empty: !selectedWeb, winner: battleState === 'complete' && battleWinner === 'web' }">
            <div class="fighter-visual">
              <img v-if="selectedImage" :src="selectedImage" :alt="selectedWeb?.name" @error="imageFailed = true">
              <div v-else class="unknown-digi">?</div>
              <span>RIVAL WEB</span>
            </div>
            <div class="fighter-copy">
              <h2>{{ selectedWeb?.name || 'SELECCIONA UN RIVAL' }}</h2>
              <div class="stat-grid">
                <div><small>NIVEL</small><b>{{ selectedWeb?.level || '—' }}</b></div>
                <div><small>ATRIBUTO</small><b>{{ selectedWeb?.attribute || '—' }}</b></div>
                <div><small>TIPO</small><b>{{ selectedWeb?.type || '—' }}</b></div>
              </div>
              <div class="attacks"><small>ATAQUES</small><span v-for="attack in selectedWeb?.attacks" :key="attack">{{ attack }}</span><em v-if="!selectedWeb?.attacks.length">—</em></div>
            </div>
          </article>

          <div class="versus" aria-hidden="true"><i /><strong>VS</strong><small>{{ battleState === 'armed' ? 'LISTO' : battleState === 'fighting' ? 'BATALLA' : battleState === 'complete' ? 'FINALIZADA' : 'EN ESPERA' }}</small></div>

          <article class="fighter-card physical-fighter" :class="{ empty: !physicalVPet, winner: battleState === 'complete' && battleWinner === 'vpet' }">
            <div class="fighter-visual"><img v-if="physicalImage" :src="physicalImage" :alt="physicalVPet?.name" @error="physicalImageFailed = true"><div v-else class="unknown-digi">?</div><span>V-PET FÍSICO</span></div>
            <div class="fighter-copy">
              <h2>{{ physicalVPet?.name || selectedModelName }}</h2>
              <div class="stat-grid">
                <div><small>NIVEL</small><b>{{ physicalVPet?.level || '—' }}</b></div><div><small>ATRIBUTO</small><b>{{ physicalVPet?.attribute || '—' }}</b></div><div><small>TIPO</small><b>{{ physicalVPet?.type || '—' }}</b></div>
              </div>
              <div class="attacks"><small>ATAQUES</small><span v-for="attack in physicalVPet?.attacks" :key="attack">{{ attack }}</span><em v-if="!physicalVPet?.attacks.length">Se cargarán al detectar el V-Pet.</em></div>
            </div>
          </article>
        </div>

        <div class="battle-footer panel">
          <span>ESTADO</span><b>{{ usbState === 'connected' ? 'BETA LINK CONECTADO · TRANSPORTE LISTO' : 'INTERFAZ LISTA · BETA LINK DESCONECTADO' }}</b>
          <span>{{ battleState === 'complete' ? 'GANADOR' : 'DATOS' }}</span><b>{{ battleState === 'complete' ? (battleWinner === 'web' ? selectedWeb?.name : physicalVPet?.name) : `${bootstrap?.counts.referenceRecords} PERFILES · ${bootstrap?.counts.protocolProfiles} PROTOCOLOS` }}<template v-if="battleProbability !== null"> · {{ (battleProbability * 100).toFixed(1) }}%</template></b>
        </div>
      </section>

      <section v-else-if="activeTab === 'probability'" class="probability-view">
        <header><p>CALCULADORA</p><h1>PROBABILIDAD<br><span>DE BATALLA</span></h1></header>
        <div class="calculator panel">
          <div class="calculator-side cyan">
            <span>RIVAL WEB</span>
            <select v-model="calculatorAttacker.level"><option v-for="level in levelOptions" :key="level">{{ level }}</option></select>
            <select v-model="calculatorAttacker.attribute"><option v-for="attribute in attributeOptions" :key="attribute">{{ attribute }}</option></select>
            <label><input v-model="calculatorAttacker.hasXAntibody" type="checkbox"> X-ANTIBODY</label>
          </div>
          <div class="probability-meter">
            <div><strong>{{ attackerPercent }}%</strong><strong>{{ 100 - attackerPercent }}%</strong></div>
            <span><i :style="{ width: `${attackerPercent}%` }" /></span>
            <small>PROBABILIDAD BASE · SIN RUIDO</small>
          </div>
          <div class="calculator-side lime">
            <span>V-PET</span>
            <select v-model="calculatorDefender.level"><option v-for="level in levelOptions" :key="level">{{ level }}</option></select>
            <select v-model="calculatorDefender.attribute"><option v-for="attribute in attributeOptions" :key="attribute">{{ attribute }}</option></select>
            <label><input v-model="calculatorDefender.hasXAntibody" type="checkbox"> X-ANTIBODY</label>
          </div>
        </div>
        <div class="breakdown-grid">
          <div class="panel"><small>NIVEL</small><b>{{ Math.round((probability?.levelProbability ?? 0) * 100) }}%</b></div>
          <div class="panel"><small>ATRIBUTO</small><b>{{ ((probability?.attributeModifier ?? 0) * 100).toFixed(0) }}%</b></div>
          <div class="panel"><small>X-ANTIBODY</small><b>{{ ((probability?.xAntibodyModifier ?? 0) * 100).toFixed(0) }}%</b></div>
          <div class="panel"><small>RUIDO CONFIGURADO</small><b>±{{ Math.round((bootstrap?.probability.noise.amplitude ?? 0) * 100) }}%</b></div>
        </div>
        <div class="probability-tables">
          <section>
            <small>NIVEL × NIVEL</small>
            <div class="matrix-wrap panel">
              <table>
                <thead><tr><th>WEB ↓ / V-PET →</th><th v-for="level in levelMatrix.headers" :key="level">{{ level }}</th></tr></thead>
                <tbody><tr v-for="row in levelMatrix.rows" :key="row.name"><th>{{ row.name }}</th><td v-for="(value, index) in row.values" :key="levelMatrix.headers[index]" :class="matrixClass(value, .5)">{{ Math.round(value * 100) }}%</td></tr></tbody>
              </table>
            </div>
          </section>
          <section>
            <small>ATRIBUTO × ATRIBUTO</small>
            <div class="matrix-wrap panel">
              <table>
                <thead><tr><th>WEB ↓ / V-PET →</th><th v-for="attribute in attributeMatrix.headers" :key="attribute">{{ attribute }}</th></tr></thead>
                <tbody><tr v-for="row in attributeMatrix.rows" :key="row.name"><th>{{ row.name }}</th><td v-for="(value, index) in row.values" :key="attributeMatrix.headers[index]" :class="matrixClass(value, 0)">{{ formatModifier(value) }}</td></tr></tbody>
              </table>
            </div>
          </section>
        </div>
      </section>

      <section v-else class="system-view">
        <header><p>DIAGNÓSTICO</p><h1>SISTEMA<br><span>EN VIVO</span></h1></header>
        <div class="system-grid">
          <article class="panel gps-panel">
            <div><span>UBICACIÓN</span><b :class="gpsState">{{ gpsState === 'active' ? 'ACTIVA' : gpsState === 'error' ? 'ERROR' : 'INACTIVA' }}</b></div>
            <dl><dt>LATITUD</dt><dd>{{ latitude?.toFixed(6) ?? '—' }}</dd><dt>LONGITUD</dt><dd>{{ longitude?.toFixed(6) ?? '—' }}</dd><dt>PRECISIÓN</dt><dd>{{ gpsAccuracy ? `${Math.round(gpsAccuracy)} m` : '—' }}</dd></dl>
            <button v-if="gpsState !== 'active'" @click="startGps">ACTIVAR GPS</button><button v-else @click="stopGps">DETENER GPS</button>
          </article>
          <article class="panel serial-panel">
            <div><span>SALIDA SERIAL</span><b>9600 BAUD</b></div>
            <pre><code v-for="(line, index) in consoleLines" :key="`${index}-${line}`">{{ line }}
</code></pre>
          </article>
        </div>
        <div v-if="error" class="error-banner">{{ error }}</div>
      </section>
    </main>
  </div>
</template>
