<script setup lang="ts">
import { ref } from 'vue'

const nombre = ref('')
const correo = ref('')
const mensaje = ref('')
const enviando = ref(false)
const estado = ref('')
const exito = ref(false)
const apiUrl = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

async function enviar() {
  enviando.value = true
  estado.value = ''
  exito.value = false

  try {
    if (!apiUrl) throw new Error('API no configurada')
    const respuesta = await fetch(`${apiUrl}/contacto`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre: nombre.value, correo: correo.value, mensaje: mensaje.value }),
    })
    if (!respuesta.ok) throw new Error('Error al enviar')
    estado.value = 'Mensaje enviado. Te responderé pronto.'
    exito.value = true
    nombre.value = ''
    correo.value = ''
    mensaje.value = ''
  } catch {
    estado.value = 'No pude enviarlo ahora. Escríbeme directamente al correo de esta sección.'
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <form class="contact-form" @submit.prevent="enviar">
    <div class="form-head"><span>ENVÍAME UN MENSAJE</span><small>RESPUESTA DIRECTA A TU CORREO</small></div>
    <label><span>01 / NOMBRE</span><input v-model="nombre" autocomplete="name" placeholder="Tu nombre" maxlength="100" required></label>
    <label><span>02 / CORREO</span><input v-model="correo" type="email" autocomplete="email" placeholder="nombre@correo.com" required></label>
    <label><span>03 / MENSAJE</span><textarea v-model="mensaje" placeholder="Cuéntame sobre tu proyecto" maxlength="3000" required /></label>
    <button type="submit" :disabled="enviando"><span>{{ enviando ? 'ENVIANDO...' : 'ENVIAR MENSAJE' }}</span><b aria-hidden="true">→</b></button>
    <p v-if="estado" class="form-status" :class="{ success: exito }" role="status">{{ estado }}</p>
  </form>
</template>

<style scoped>
.contact-form{display:grid;gap:0}.form-head{align-items:end;border-bottom:1px solid rgba(255,255,255,.45);display:flex;justify-content:space-between;padding:0 0 1.5rem}.form-head span{font:600 1.1rem 'Space Grotesk',sans-serif}.form-head small,label>span{font:400 .6rem 'DM Mono',monospace;letter-spacing:.12em}.contact-form label{border-bottom:1px solid rgba(255,255,255,.35);display:grid;gap:.7rem;padding:1.35rem 0}.contact-form input,.contact-form textarea{background:transparent;border:0;border-radius:0;color:white;font:400 1rem 'Space Grotesk',sans-serif;outline:0;padding:0;resize:vertical;width:100%}.contact-form input::placeholder,.contact-form textarea::placeholder{color:rgba(255,255,255,.58)}.contact-form textarea{min-height:110px}.contact-form label:focus-within{border-color:white}.contact-form button{align-items:center;background:white;border:0;color:var(--purple-dark);cursor:pointer;display:flex;font:600 .76rem 'DM Mono',monospace;justify-content:space-between;letter-spacing:.08em;margin-top:1.5rem;padding:1rem 1.2rem;transition:.25s}.contact-form button:hover{background:var(--ink);color:white;transform:translate(-3px,-3px)}.contact-form button:disabled{cursor:wait;opacity:.65}.contact-form button b{font-size:1.35rem}.form-status{font:400 .72rem/1.5 'DM Mono',monospace;margin:1rem 0 0}.form-status.success{color:#d8ff9c}@media(max-width:600px){.form-head{align-items:start;flex-direction:column;gap:.5rem}}
</style>
