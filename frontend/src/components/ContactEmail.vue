
<script setup lang="ts">
import { ref } from 'vue'

const nombre = ref('')
const correo = ref('')
const mensaje = ref('')
const enviando = ref(false)
const estado = ref('')

async function enviar() {
  enviando.value = true
  estado.value = ''

  try {
    const respuesta = await fetch(
      `${import.meta.env.VITE_API_URL}/contacto`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          nombre: nombre.value,
          correo: correo.value,
          mensaje: mensaje.value
        })
      }
    )

    if (!respuesta.ok) {
      throw new Error('Error al enviar')
    }

    estado.value = '¡Mensaje enviado correctamente!'
    nombre.value = ''
    correo.value = ''
    mensaje.value = ''
  } catch {
    estado.value = 'No se pudo enviar el mensaje.'
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <form @submit.prevent="enviar">
    <h2>Contáctanos</h2>

    <input
      v-model="nombre"
      placeholder="Tu nombre"
      maxlength="100"
      required
    />

    <input
      v-model="correo"
      type="email"
      placeholder="Tu correo"
      required
    />

    <textarea
      v-model="mensaje"
      placeholder="Escribe tu mensaje"
      maxlength="3000"
      required
    />

    <button type="submit" :disabled="enviando">
      {{ enviando ? 'Enviando...' : 'Enviar mensaje' }}
    </button>

    <p role="status">{{ estado }}</p>
  </form>
</template>
