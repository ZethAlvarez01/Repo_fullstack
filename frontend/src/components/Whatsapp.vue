<script setup lang="ts">
import whatsappIcon from '../icons/whatsapp.png'

const telefono = '525547131440'
const mensaje = encodeURIComponent('Hola Zeth, vi tu portafolio y me gustaría platicarte sobre un proyecto.')
const whatsappUrl = `https://wa.me/${telefono}?text=${mensaje}`
</script>

<template>
  <a class="whatsapp-button" :href="whatsappUrl" target="_blank" rel="noopener noreferrer" aria-label="Contactar a Zeth por WhatsApp" title="Escríbeme por WhatsApp">
    <span class="button-label">WHATSAPP</span><img :src="whatsappIcon" alt="" aria-hidden="true">
  </a>
</template>

<style scoped>
.whatsapp-button{align-items:center;bottom:clamp(1rem,3vw,2rem);display:flex;gap:.7rem;position:fixed;right:clamp(1rem,3vw,2rem);text-decoration:none;z-index:1000}.button-label{background:var(--ink);color:white;font:600 .6rem 'DM Mono',monospace;letter-spacing:.1em;opacity:0;padding:.6rem .75rem;transform:translateX(8px);transition:.25s}.whatsapp-button img{display:block;filter:drop-shadow(0 7px 11px rgba(30,20,45,.24));height:58px;object-fit:contain;transition:.25s;width:58px}.whatsapp-button:hover .button-label{opacity:1;transform:none}.whatsapp-button:hover img{transform:translateY(-3px) scale(1.05)}.whatsapp-button:focus-visible{outline:3px solid var(--purple);outline-offset:5px}@media(max-width:600px){.button-label{display:none}.whatsapp-button img{height:52px;width:52px}}@media(prefers-reduced-motion:reduce){.button-label,.whatsapp-button img{transition:none}}
</style>
