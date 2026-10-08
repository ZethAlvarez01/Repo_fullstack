<script setup lang="ts">
import Child from './components/Child.vue';
import ConexionAPI from './components/ConexionAPI.vue';
import ContactEmail from './components/ContactEmail.vue';
import Test from './components/Test.vue';
import Test2 from './components/Test2.vue';
import Whatsapp from './components/Whatsapp.vue';

const variable_deL_papa = "Hola soy el papa"
const person = {
  nombre:"Zeth",
  age:30
}

</script>

<template>
  <Test></Test>
  <Test2></Test2>
  <Child :mensaje="variable_deL_papa" :person="person" ></Child>

  <p>Fin de la seccion de pruebas</p>

  <ConexionAPI></ConexionAPI>

  <hr>

  <Whatsapp></Whatsapp>

  <hr>

  <ContactEmail></ContactEmail>

</template>
