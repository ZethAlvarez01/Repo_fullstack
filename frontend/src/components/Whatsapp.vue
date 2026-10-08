<script setup lang="ts">
const telefono = '525547131440'

const mensaje = encodeURIComponent(
  'Hola, vi su página web y me gustaría conocer sus productos.'
)

const whatsappUrl = `https://wa.me/${telefono}?text=${mensaje}`
</script>

<template>
  <a
    :href="whatsappUrl"
    target="_blank"
    rel="noopener noreferrer"
  >
    Contactar por WhatsApp
  </a>
</template>