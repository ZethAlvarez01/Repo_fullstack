<script setup lang="ts">
import whatsappIcon from '../icons/whatsapp.png'

const telefono = '525547131440'

const mensaje = encodeURIComponent(
  'Hola, vi su página web y me gustaría conocer sus productos.'
)

const whatsappUrl = `https://wa.me/${telefono}?text=${mensaje}`
</script>

<template>
  <a
    class="whatsapp-button"
    :href="whatsappUrl"
    target="_blank"
    rel="noopener noreferrer"
    aria-label="Enviar un mensaje por WhatsApp"
    title="Contáctame por WhatsApp"
  >
    <img :src="whatsappIcon" alt="" aria-hidden="true">
  </a>
</template>

<style scoped>
.whatsapp-button {
  align-items: center;
  background: transparent;
  border-radius: 50%;
  bottom: clamp(1rem, 3vw, 2rem);
  display: flex;
  filter: drop-shadow(0 6px 10px rgb(22 19 29 / 24%));
  height: 64px;
  justify-content: center;
  position: fixed;
  right: clamp(1rem, 3vw, 2rem);
  transition: filter .2s ease, transform .2s ease;
  width: 64px;
  z-index: 1000;
}

.whatsapp-button img {
  display: block;
  height: 100%;
  object-fit: contain;
  width: 100%;
}

.whatsapp-button:hover {
  filter: drop-shadow(0 9px 14px rgb(22 19 29 / 32%));
  transform: translateY(-3px) scale(1.06);
}

.whatsapp-button:focus-visible {
  outline: 3px solid #8257f6;
  outline-offset: 4px;
}

.whatsapp-button:active {
  transform: scale(.96);
}

@media (max-width: 600px) {
  .whatsapp-button {
    height: 56px;
    width: 56px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .whatsapp-button {
    transition: none;
  }
}
</style>
