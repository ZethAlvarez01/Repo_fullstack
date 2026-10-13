<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import SiteHeader from './components/SiteHeader.vue'
import luminaImage from './assets/projects/lumina-ribbon.png'
import pulseImage from './assets/projects/pulse-race.png'

const x = ref(0)
const y = ref(0)
function track(event: PointerEvent) { x.value = event.clientX; y.value = event.clientY }

onMounted(() => {
  window.addEventListener('pointermove', track, { passive: true })
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible') })
  }, { threshold: .12 })
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el))
})
onBeforeUnmount(() => window.removeEventListener('pointermove', track))
</script>

<template>
  <div class="crosshair" :style="{ transform: `translate(${x}px, ${y}px)` }"><i/><b/></div>
  <SiteHeader />
  <main>
    <section id="inicio" class="dashboard-hero page-grid">
      <div class="hero-code reveal">
        <span class="window-bar"><i/><i/><i/><b>portfolio_index.vue</b></span>
        <pre><code><span class="purple">const</span> developer = {
  name: <span class="green">'Zeth Alvarez'</span>,
  focus: [<span class="green">'frontend'</span>, <span class="green">'motion'</span>],
  status: <span class="purple">'available'</span>
}</code></pre>
        <div class="status"><i/> SISTEMA DISPONIBLE</div>
      </div>

      <div class="hero-identity reveal">
        <p>PORTAFOLIO / 2026</p>
        <h1>ZETH<br/><span>ALVAREZ</span></h1>
        <div class="role"><b>FRONTEND</b><b>DESIGN</b><b>MOTION</b></div>
      </div>

      <aside class="hero-note reveal">
        <span>00 / INTRO</span>
        <p>Diseño y desarrollo experiencias web con carácter, claridad y movimiento.</p>
        <a href="#proyectos">Explorar trabajo ↘</a>
      </aside>

      <div class="coordinates">19.4326° N &nbsp; / &nbsp; 99.1332° W</div>
    </section>

    <section id="proyectos" class="projects-section page-grid">
      <div class="section-head reveal">
        <span>01 / SELECTED WORK</span>
        <h2>PROYECTOS<br/>EN PRODUCCIÓN</h2>
        <p>Dos identidades, dos ritmos y una misma atención al detalle. Ahora corren dentro de este mismo servidor.</p>
      </div>

      <div class="project-grid">
        <a class="project-window lumina reveal" href="/lumina.html">
          <div class="browser-top"><span><i/><i/><i/></span><code>/lumina.html</code><b>01</b></div>
          <div class="project-visual">
            <div class="scan-grid"/>
            <img :src="luminaImage" alt="Vista previa del proyecto Lúmina"/>
            <span class="launch">ENTRAR ↗</span>
          </div>
          <div class="project-caption"><div><h3>LÚMINA</h3><p>Estudio creativo / Experiencia editorial</p></div><span>VUE · SCROLL · 3D</span></div>
        </a>

        <a class="project-window pulse reveal" href="/pulse.html">
          <div class="browser-top"><span><i/><i/><i/></span><code>/pulse.html</code><b>02</b></div>
          <div class="project-visual">
            <img :src="pulseImage" alt="Vista previa del proyecto Pulse Events"/>
            <div class="race-overlay">GO<span>!</span></div>
            <span class="launch">ENTRAR ↗</span>
          </div>
          <div class="project-caption"><div><h3>PULSE EVENTS</h3><p>Eventos deportivos / Experiencia cinética</p></div><span>VUE · MOTION · ART DIRECTION</span></div>
        </a>
      </div>
    </section>

    <section id="sobre-mi" class="profile page-grid">
      <div class="profile-title reveal"><span>02 / PROFILE</span><h2>DISEÑO LA IDEA.<br/>PROGRAMO<br/>LA <em>EXPERIENCIA.</em></h2></div>
      <div class="profile-card reveal"><span>[ ACERCA DE MÍ ]</span><p>Trabajo en el punto donde la interfaz, la identidad y el código se encuentran. Me interesa que cada proyecto tenga una lógica clara y una presencia propia.</p></div>
      <div class="profile-card accent reveal"><span>[ ENFOQUE ]</span><p>Frontend creativo, sistemas visuales, narrativa de scroll, microinteracciones y conexiones con APIs.</p></div>
    </section>

    <section id="habilidades" class="stack page-grid">
      <div class="stack-title reveal"><span>03 / STACK</span><h2>CAPACIDADES</h2></div>
      <div class="stack-grid">
        <article class="reveal"><b>01</b><h3>Vue.js</h3><p>Componentes y experiencias reactivas.</p></article>
        <article class="reveal"><b>02</b><h3>TypeScript</h3><p>Código predecible y mantenible.</p></article>
        <article class="reveal"><b>03</b><h3>UI / UX</h3><p>Jerarquía, sistemas y detalle visual.</p></article>
        <article class="reveal"><b>04</b><h3>Motion</h3><p>Movimiento que explica y acompaña.</p></article>
        <article class="reveal"><b>05</b><h3>APIs</h3><p>Interfaces conectadas a datos reales.</p></article>
        <article class="reveal"><b>06</b><h3>Deploy</h3><p>Construcción y entrega de principio a fin.</p></article>
      </div>
    </section>

    <footer id="contacto" class="footer-grid page-grid">
      <div><span>04 / CONTACT</span><h2>LET'S<br/>BUILD<span>_</span></h2></div>
      <div class="contact-panel"><p>¿Tienes una idea, producto o experiencia que necesita cobrar vida?</p><a href="mailto:hola@zeth.dev">HOLA@ZETH.DEV ↗</a></div>
      <div class="footer-line"><span>ZETH ALVAREZ © 2026</span><span>FRONTEND / DESIGN / MOTION</span><a href="#inicio">TOP ↑</a></div>
    </footer>
  </main>
</template>
