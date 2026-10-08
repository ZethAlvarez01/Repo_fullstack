<script lang="ts" setup>
    defineProps({
        mensaje: String,
        person: Object
    })
</script>

<template>
    <h1>Mensaje del hijo</h1>

    <p>{{ mensaje }}</p>

    <div>{{ person?.nombre }}</div>

</template>

<style scoped></style>