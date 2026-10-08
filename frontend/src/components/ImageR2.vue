
<script setup lang="ts">
import { ref } from 'vue'

const API_URL = import.meta.env.VITE_API_URL

const imagenUrl = `${API_URL}/imagen-prueba`

const error = ref(false)
const cargando = ref(true)
</script>

<template>
  <section class="r2-demo">
    <h2>Mi primera imagen desde Cloudflare R2 ☁️</h2>

    <p v-if="cargando && !error">Cargando imagen...</p>

    <img
      v-show="!error"
      :src="imagenUrl"
      alt="Imagen de Digimon almacenada en Cloudflare R2"
      @load="cargando = false"
      @error="error = true; cargando = false"
    />

    <p v-if="error">
      No se pudo cargar la imagen desde FastAPI.
    </p>
  </section>
</template>

<style scoped>
.r2-demo {
  max-width: 650px;
  margin: 3rem auto;
  padding: 2rem;
  text-align: center;
}

.r2-demo img {
  display: block;
  width: 100%;
  height: auto;
  margin-top: 1.5rem;
  border: 2px solid #8b5cf6;
  border-radius: 12px;
}

.r2-demo h2 {
  color: #8b5cf6;
}
</style>
