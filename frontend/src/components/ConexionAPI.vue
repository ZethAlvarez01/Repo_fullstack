<script lang="ts" setup>

    import { onMounted, ref } from 'vue';

    type Producto ={
        "_id": string,
        "nombre": string,
        "precio": number,
        "imageUrl": string,
        "creadoEn": string

    }

    const productos = ref<Producto[]>([])

    onMounted(async () =>{
        const respuesta = await fetch(`${import.meta.env.VITE_API_URL}/datos`)
        productos.value = await respuesta.json()

    })

</script>


<template>
    <p v-for="dato in productos" :key="dato.nombre">{{ dato.nombre }} {{ dato.precio }}</p>
</template>

<style lang="css"></style>
