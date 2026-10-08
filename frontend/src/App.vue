<script setup lang="ts">
import Child from './components/Child.vue';
import ConexionAPI from './components/ConexionAPI.vue';
import ContactEmail from './components/ContactEmail.vue';
import Test from './components/Test.vue';
import Test2 from './components/Test2.vue';
import Whatsapp from './components/Whatsapp.vue';
import SiteHeader from './components/SiteHeader.vue';
import ImageR2 from './components/ImageR2.vue';
import Crear from './components/Crear.vue';

const variable_deL_papa = "Hola soy el papa"
const person = {
  nombre:"Zeth",
  age:30
}

</script>

<template>
  <SiteHeader />
  <Test></Test>
  <Test2></Test2>
  <Child :mensaje="variable_deL_papa" :person="person" ></Child>

  <p>Fin de la seccion de pruebas</p>

  <ConexionAPI></ConexionAPI>

  <hr>

  <Whatsapp></Whatsapp>

  <hr>

  <ContactEmail></ContactEmail>

  <hr>

  <ImageR2></ImageR2>

  <Crear></Crear>

</template>
