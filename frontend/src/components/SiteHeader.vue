<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const menuOpen = ref(false)
const activeLink = ref('#inicio')

const links = [
  { label: 'inicio', href: '#inicio' },
  { label: 'sobre mí', href: '#sobre-mi' },
  { label: 'proyectos', href: '#proyectos' },
  { label: 'capacidades', href: '#habilidades' },
  { label: 'contacto', href: '#contacto' },
]

function selectLink(href: string) {
  activeLink.value = href
  menuOpen.value = false
}

function updateActiveSection() {
  const current = [...links].reverse().find(({ href }) => {
    const section = document.querySelector(href)
    return section && section.getBoundingClientRect().top <= 160
  })
  if (current) activeLink.value = current.href
}

onMounted(() => window.addEventListener('scroll', updateActiveSection, { passive: true }))
onBeforeUnmount(() => window.removeEventListener('scroll', updateActiveSection))
</script>

<template>
  <header class="site-header">
    <a class="brand" href="#inicio" aria-label="Ir al inicio" @click="selectLink('#inicio')">
      <span class="brand-mark" aria-hidden="true"><i /><i /><i /><i /></span>
      <span>ZETH.DEV</span>
    </a>

    <nav class="desktop-nav" aria-label="Navegación principal">
      <a v-for="(link, index) in links" :key="link.href" :class="{ active: activeLink === link.href }" :href="link.href" @click="selectLink(link.href)">
        <small>0{{ index + 1 }}</small>{{ link.label }}
      </a>
    </nav>

    <button class="menu-toggle" :class="{ open: menuOpen }" type="button" :aria-expanded="menuOpen" aria-controls="mobile-nav" :aria-label="menuOpen ? 'Cerrar menú' : 'Abrir menú'" @click="menuOpen = !menuOpen">
      <span /><span />
    </button>

    <nav id="mobile-nav" class="mobile-nav" :class="{ open: menuOpen }" aria-label="Navegación móvil">
      <a v-for="(link, index) in links" :key="link.href" :class="{ active: activeLink === link.href }" :href="link.href" @click="selectLink(link.href)">
        <small>0{{ index + 1 }}</small>{{ link.label }}
      </a>
    </nav>
  </header>
</template>

<style scoped>
.site-header{align-items:center;background:rgba(247,245,242,.94);border-bottom:1px solid var(--line);display:flex;height:70px;justify-content:space-between;padding:0 var(--page);position:sticky;top:0;z-index:100;backdrop-filter:blur(14px)}
.brand{align-items:center;display:flex;font:700 1rem 'Space Grotesk',sans-serif;gap:.75rem;letter-spacing:.04em;text-decoration:none}.brand-mark{display:grid;gap:2px;grid-template-columns:repeat(2,5px);transform:rotate(45deg)}.brand-mark i{background:var(--purple);display:block;height:5px;width:5px}
.desktop-nav{align-items:stretch;display:flex;height:100%;gap:2.2rem}.desktop-nav a,.mobile-nav a{align-items:center;display:flex;font:500 .72rem 'DM Mono',monospace;gap:.55rem;text-decoration:none;text-transform:uppercase;transition:color .2s}.desktop-nav small,.mobile-nav small{color:var(--muted);font-size:.55rem}.desktop-nav a:hover,.desktop-nav a.active,.mobile-nav a.active{color:var(--purple)}
.menu-toggle{background:none;border:0;cursor:pointer;display:none;height:42px;position:relative;width:42px}.menu-toggle span{background:var(--ink);height:2px;left:8px;position:absolute;transition:.25s;width:26px}.menu-toggle span:first-child{top:15px}.menu-toggle span:last-child{top:25px}.menu-toggle.open span:first-child{top:20px;transform:rotate(45deg)}.menu-toggle.open span:last-child{top:20px;transform:rotate(-45deg)}.mobile-nav{display:none}
@media(max-width:850px){.desktop-nav{display:none}.menu-toggle{display:block}.mobile-nav{background:var(--paper);border-bottom:1px solid var(--line);display:grid;gap:1.1rem;left:0;opacity:0;padding:1.7rem var(--page);pointer-events:none;position:absolute;top:100%;transform:translateY(-10px);transition:.25s;width:100%}.mobile-nav.open{opacity:1;pointer-events:auto;transform:none}.mobile-nav a{font-size:.85rem}}
</style>
