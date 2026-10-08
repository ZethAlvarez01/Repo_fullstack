
<script setup lang="ts">
import { onMounted, ref } from 'vue'

const API_URL = import.meta.env.VITE_API_URL

interface Producto {
  id: string
  nombre: string
  descripcion: string
  precio: number
  imagen_key: string | null
}

const productos = ref<Producto[]>([])

onMounted(async () => {
  const respuesta = await fetch(`${API_URL}/productos`)
  productos.value = await respuesta.json()
})
</script>

<template>
  <section>
    <h2>Mis productos 💜</h2>

    <div v-for="producto in productos" :key="producto.id">
      <img
        v-if="producto.imagen_key"
        :src="`${API_URL}/productos/${producto.id}/imagen`"
        :alt="producto.nombre"
        width="200"
      />

      <h3>{{ producto.nombre }}</h3>
      <p>{{ producto.descripcion }}</p>
      <strong>${{ producto.precio }}</strong>

      <hr />
    </div>
  </section>
</template>
