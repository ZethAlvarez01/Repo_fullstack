<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import ContactEmail from './components/ContactEmail.vue'
import SiteHeader from './components/SiteHeader.vue'
import Whatsapp from './components/Whatsapp.vue'
import luminaImage from './assets/projects/lumina-ribbon.png'
import pulseImage from './assets/projects/pulse-race.png'
import lumeImage from './assets/projects/lume-beauty.png'

const pointerX = ref(0)
const pointerY = ref(0)
const scrollProgress = ref(0)
let observer: IntersectionObserver | undefined
let ticking = false

function updatePointer(event: PointerEvent) {
  pointerX.value = event.clientX
  pointerY.value = event.clientY
}

function updateScroll() {
  if (ticking) return
  ticking = true
  requestAnimationFrame(() => {
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight
    scrollProgress.value = maxScroll > 0 ? window.scrollY / maxScroll : 0
    ticking = false
  })
}

onMounted(() => {
  window.addEventListener('pointermove', updatePointer, { passive: true })
  window.addEventListener('scroll', updateScroll, { passive: true })
  window.addEventListener('resize', updateScroll, { passive: true })
  updateScroll()

  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add('visible')
    })
  }, { threshold: 0.12 })

  document.querySelectorAll('.reveal').forEach((element) => observer?.observe(element))
})

onBeforeUnmount(() => {
  window.removeEventListener('pointermove', updatePointer)
  window.removeEventListener('scroll', updateScroll)
  window.removeEventListener('resize', updateScroll)
  observer?.disconnect()
})
</script>

<template>
  <div class="scroll-progress" :style="{ transform: `scaleX(${scrollProgress})` }" />
  <div class="pointer-pixel" :style="{ transform: `translate3d(${pointerX}px, ${pointerY}px, 0)` }" />
  <SiteHeader />

  <main>
    <section id="inicio" class="hero section-shell">
      <div class="hero-copy reveal">
        <p class="eyebrow">PORTAFOLIO / 2026</p>
        <h1>ZETH<br><span>ALVAREZ</span></h1>
        <p class="hero-role">FRONTEND / BACKEND / DATA</p>
      </div>

      <div class="hero-pixels" aria-hidden="true">
        <i v-for="pixel in 18" :key="pixel" />
      </div>

      <div class="hero-bottom reveal">
        <p>Construyo productos digitales claros, funcionales y con una identidad que no se pierde entre plantillas.</p>
        <a href="#proyectos">Ver proyectos <span>↓</span></a>
      </div>
    </section>

    <section id="sobre-mi" class="about section-shell">
      <p class="section-label reveal">01 / SOBRE MÍ</p>
      <div class="about-layout">
        <h2 class="reveal">IDEAS CLARAS.<br>CÓDIGO SÓLIDO.<br><em>PRODUCTOS ÚTILES.</em></h2>
        <div class="about-copy reveal pixel-frame">
          <span class="pixel-cluster top-left" aria-hidden="true" />
          <p>Soy desarrollador de software enfocado en convertir necesidades reales en interfaces, servicios y sistemas que se sienten simples al usarlos.</p>
          <p>Trabajo desde la experiencia visual hasta la arquitectura, los datos y la entrega del producto.</p>
          <span class="pixel-cluster bottom-right" aria-hidden="true" />
        </div>
      </div>
    </section>

    <section id="proyectos" class="work section-shell">
      <div class="section-heading reveal">
        <p class="section-label">02 / TRABAJO SELECCIONADO</p>
        <h2>PROYECTOS</h2>
      </div>

      <div class="project-list">
        <a class="project-card reveal" href="/lumina.html">
          <div class="project-image project-image-lumina">
            <img :src="luminaImage" alt="Vista previa del proyecto Lúmina">
            <span class="pixel-cluster top-left" aria-hidden="true" />
            <span class="pixel-cluster bottom-right" aria-hidden="true" />
          </div>
          <div class="project-copy">
            <span>01 / ESTUDIO DIGITAL</span>
            <h3>LÚMINA</h3>
            <p>Una experiencia editorial inmersiva donde la identidad y la tecnología construyen una atmósfera propia.</p>
            <div><small>VUE · INTERACCIÓN · UI</small><b aria-hidden="true">→</b></div>
          </div>
        </a>

        <a class="project-card reveal" href="/pulse.html">
          <div class="project-image">
            <img :src="pulseImage" alt="Vista previa del proyecto Pulse Events">
            <span class="pixel-cluster top-left" aria-hidden="true" />
            <span class="pixel-cluster bottom-right" aria-hidden="true" />
          </div>
          <div class="project-copy">
            <span>02 / EVENTOS DEPORTIVOS</span>
            <h3>PULSE EVENTS</h3>
            <p>Una plataforma deportiva dinámica con recorridos, eventos anteriores y próximas experiencias.</p>
            <div><small>VUE · SCROLL · EXPERIENCIA WEB</small><b aria-hidden="true">→</b></div>
          </div>
        </a>

        <a class="project-card project-card-lume reveal" href="/lume.html">
          <div class="project-image project-image-lume">
            <img :src="lumeImage" alt="Vista previa del proyecto Lumé">
            <span class="pixel-cluster top-left" aria-hidden="true" />
            <span class="pixel-cluster bottom-right" aria-hidden="true" />
          </div>
          <div class="project-copy">
            <span>03 / BELLEZA CONSCIENTE</span>
            <h3>LUMÉ</h3>
            <p>Una experiencia delicada de autocuidado con un espejo interactivo que utiliza la cámara del dispositivo.</p>
            <div><small>VUE · CÁMARA · EXPERIENCIA WEB</small><b aria-hidden="true">→</b></div>
          </div>
        </a>
      </div>
    </section>

    <section id="habilidades" class="skills section-shell">
      <div class="section-heading reveal">
        <p class="section-label">03 / CAPACIDADES</p>
        <h2>STACK</h2>
      </div>

      <div class="skill-list">
        <article class="reveal"><span>01</span><h3>Frontend</h3><p>Vue, TypeScript, interfaces responsivas y experiencias accesibles.</p></article>
        <article class="reveal"><span>02</span><h3>Backend</h3><p>APIs, servicios, autenticación y lógica de negocio mantenible.</p></article>
        <article class="reveal"><span>03</span><h3>Data Science</h3><p>Análisis, transformación y visualización de datos para tomar decisiones.</p></article>
        <article class="reveal"><span>04</span><h3>Software Engineering</h3><p>Arquitectura, pruebas, integración, despliegue y evolución de productos.</p></article>
      </div>
    </section>

    <section id="contacto" class="contact section-shell">
      <div class="contact-heading reveal">
        <p class="section-label">04 / CONTACTO</p>
        <h2>HAGAMOS<br><em>ALGO ÚTIL.</em></h2>
        <a class="email-link" href="mailto:zethalvarezh@hotmail.com">ZETHALVAREZH@HOTMAIL.COM <span>↗</span></a>
      </div>

      <div class="contact-form-wrap reveal pixel-frame">
        <span class="pixel-cluster top-left" aria-hidden="true" />
        <ContactEmail />
        <span class="pixel-cluster bottom-right" aria-hidden="true" />
      </div>

      <div class="contact-bottom">
        <span>ZETH ALVAREZ © 2026</span>
        <span>SOFTWARE ENGINEER / CDMX</span>
        <a href="#inicio">VOLVER ARRIBA ↑</a>
      </div>
    </section>
  </main>

  <Whatsapp />
</template>
