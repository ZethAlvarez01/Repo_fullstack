<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { referenceImageUrl } from './data/client'
import type { ReferenceProfile } from './data/types'

const props = defineProps<{ profile: ReferenceProfile | null; label: string }>()
const imageIndex = ref(0)
const imageFailed = ref(false)
const notice = ref('')
const imageCount = computed(() => props.profile?.images?.length || (props.profile?.image ? 1 : 0))
const imageUrl = computed(() => referenceImageUrl(props.profile, imageIndex.value))
const imageLabel = computed(() => props.profile?.images?.[imageIndex.value]?.label || 'Ilustración 1')

watch(() => props.profile?.id, () => {
  imageIndex.value = 0
  imageFailed.value = false
  notice.value = ''
})

function changeImage(direction: number) {
  if (imageCount.value < 2) return
  imageIndex.value = (imageIndex.value + direction + imageCount.value) % imageCount.value
  imageFailed.value = false
  notice.value = ''
}

function handleImageError() {
  if (imageIndex.value > 0) {
    imageIndex.value = 0
    notice.value = 'No se pudo cargar esta ilustración.'
    return
  }
  imageFailed.value = true
}
</script>

<template>
  <div class="fighter-visual">
    <img
      v-if="imageUrl && !imageFailed"
      :key="imageUrl"
      :src="imageUrl"
      :alt="`${profile?.name} · ${imageLabel}`"
      @error="handleImageError"
    >
    <div v-else class="unknown-digi">?</div>
    <span>{{ label }}</span>
    <div v-if="imageCount > 1" class="illustration-controls" :aria-label="`Ilustraciones de ${profile?.name}`">
      <button type="button" :aria-label="`Ilustración anterior de ${profile?.name}`" @click="changeImage(-1)">‹</button>
      <small aria-live="polite" aria-atomic="true">{{ imageIndex + 1 }} / {{ imageCount }}</small>
      <button type="button" :aria-label="`Ilustración siguiente de ${profile?.name}`" @click="changeImage(1)">›</button>
    </div>
    <small v-if="notice" class="illustration-notice" role="status">{{ notice }}</small>
  </div>
</template>

<style scoped>
.illustration-controls{position:absolute;right:10px;bottom:10px;display:flex;align-items:center;background:rgba(5,11,18,.94);border:1px solid var(--line);color:var(--cyan);box-shadow:0 3px 12px #0002}
.illustration-controls button{display:grid;place-items:center;width:44px;height:44px;background:transparent;border:0;color:inherit;font-size:1.8rem;cursor:pointer;touch-action:manipulation}
.illustration-controls button:hover{background:#163447}
.illustration-controls button:focus-visible{outline:2px solid currentColor;outline-offset:-3px}
.illustration-controls small{min-width:46px;text-align:center;font:500 .65rem 'DM Mono',monospace;white-space:nowrap}
.illustration-notice{position:absolute;top:10px;left:10px;right:10px;padding:8px 10px;background:rgba(5,11,18,.94);color:var(--amber);font:.65rem 'DM Mono',monospace}
</style>
