<script setup lang="ts">
import Child from './components/Child.vue';
import ConexionAPI from './components/ConexionAPI.vue';
import Test from './components/Test.vue';
import Test2 from './components/Test2.vue';


</script>

<template>
  <Test></Test>
  <Test2></Test2>
  <Child mensaje="Este es mensaje del padre"></Child>

  <p>Fin de la seccion de pruebas</p>

  <ConexionAPI></ConexionAPI>

</template>
