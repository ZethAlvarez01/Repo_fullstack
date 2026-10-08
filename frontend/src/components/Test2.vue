<script lang="ts" setup>
import { ref } from 'vue';

    const variable = ref(true);

    const change = () => {
        variable.value = !variable.value
    }

    const arreglo = ["1","2","3","4","5","6","7","8"]

    const objeto = [
        {id:1,nombre:"Zeth",tarjeta:"1234-12"},
        {id:2,nombre:"Maria",tarjeta:"5232-13"},
        {id:3,nombre:"Jair",tarjeta:"2335-14"}
    ]

</script>

<template>
<h1 :class="variable ? 'class_color' : 'class_color2'">Adios</h1>
<button @click="change">Boton</button>

<h3 v-if="variable">Prueba de if</h3>

<h2 v-for="num in arreglo" :key="num">{{ num }}</h2>

<h2 v-for="(num,index) in arreglo">{{ index }} {{num }}</h2>

<ul>
    <li v-for="persona in objeto" :key="persona.id">{{ persona.nombre }}</li>
</ul>

</template>

<style>
    .class_color {
        color: brown;
    }

    .class_color2 {
        color: cornflowerblue
    }
</style>