<script lang="ts" setup>
    defineProps({
        mensaje: String
    })
</script>

<template>
    <h1>Mensaje del hijo</h1>

    <p>{{ mensaje }}</p>

</template>

<style scoped></style>