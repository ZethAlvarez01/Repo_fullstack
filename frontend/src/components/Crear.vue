<script setup lang="ts">
import { ref } from 'vue'
import Listar from './Listar.vue'

const nombre = ref('')
const descripcion = ref('')
const precio = ref<number | null>(null)
const imagen = ref<File | null>(null)
const listaVersion = ref(0)

function seleccionarImagen(event: Event) {
  const input = event.target as HTMLInputElement
  imagen.value = input.files?.[0] ?? null
}

const API_URL = import.meta.env.VITE_API_URL

async function subirImagen() {
  if (!imagen.value) {
    alert('Selecciona una imagen')
    return
  }

  const datos = new FormData()
  datos.append('imagen', imagen.value)

  const respuesta = await fetch(`${API_URL}/productos/imagen`, {
    method: 'POST',
    body: datos
  })

  if (!respuesta.ok) {
    alert('Error al subir la imagen')
    return
  }

  const resultado = await respuesta.json()

    const respuestaProducto = await fetch(`${API_URL}/productos`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        nombre: nombre.value,
        descripcion: descripcion.value,
        precio: precio.value,
        imagen_key: resultado.imagen_key
    })
    })

    if (respuestaProducto.ok) {
      listaVersion.value += 1
    }

    if (!respuestaProducto.ok) {
    alert('La imagen se subió a R2, pero no se guardó el producto en MongoDB')
    return
    }

    alert('¡Producto e imagen guardados correctamente! 💜')
}

</script>

<template>
  <section>
    <h2>Agregar producto 💜</h2>

    <form @submit.prevent="subirImagen">
      <input v-model="nombre" placeholder="Nombre" required />

      <textarea
        v-model="descripcion"
        placeholder="Descripción"
      />

      <input
        v-model.number="precio"
        type="number"
        min="0"
        step="0.01"
        placeholder="Precio"
        required
      />

      <input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        @change="seleccionarImagen"
        required
      />

      <button type="submit">
        Guardar producto
        </button>
    </form>
  </section>

    <hr>

  <Listar :key="listaVersion" />


</template>
