import type { CatalogFamily, ReferenceProfile, ReferenceSearchResult, VPetBootstrap } from './types'

export const apiBase = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, { headers: { Accept: 'application/json' } })
  if (!response.ok) throw new Error(`V-Pet API ${response.status}: ${response.statusText}`)
  return response.json() as Promise<T>
}

export function loadVPetBootstrap(): Promise<VPetBootstrap> {
  return request('/api/vpet/bootstrap')
}

export function loadCatalogFamily(family: string, includeReference = false): Promise<CatalogFamily> {
  const suffix = includeReference ? '?include_reference=true' : ''
  return request(`/api/vpet/catalog/${encodeURIComponent(family)}${suffix}`)
}

export function loadVPetConfig<T>(name: string): Promise<T> {
  return request(`/api/vpet/config/${encodeURIComponent(name)}`)
}

export function searchReferenceBook(query = '', offset = 0, limit = 50): Promise<ReferenceSearchResult> {
  const params = new URLSearchParams({ query, offset: String(offset), limit: String(limit) })
  return request(`/api/vpet/reference?${params}`)
}

export async function loadReferenceVariants(name: string): Promise<ReferenceProfile[]> {
  const result = await request<{ variants: ReferenceProfile[] }>(`/api/vpet/reference/${encodeURIComponent(name)}`)
  return result.variants
}

export function referenceImageUrl(profile: ReferenceProfile | null, imageIndex = 0): string {
  const filename = profile?.images?.[imageIndex]?.filename ?? profile?.image
  if (!filename) return ''
  return `${apiBase}/api/vpet/images/${encodeURIComponent(filename)}`
}
