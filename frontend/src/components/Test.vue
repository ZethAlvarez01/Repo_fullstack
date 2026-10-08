<script lang="ts" setup>
import { ref } from 'vue';

    const variable = ref(0);

    const addOne = () =>{
        variable.value++;
    }

    const myId = "patata_short"
    let myValue = ref("some value")

</script>

<template>
   <h1>Hola</h1>
   <p>variable {{variable}}</p>
    <h2>{{ myValue }}</h2>
   <h2 :id="myId">Patata</h2>

   <input type="text" v-model="myValue">

   <button @click="addOne">Prueba</button>
   <button v-on:click="addOne">Boton cliqueame</button>
</template>

<style scoped>

</style>