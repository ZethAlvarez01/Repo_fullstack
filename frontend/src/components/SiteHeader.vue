<script setup lang="ts">
import { ref } from 'vue'

const menuOpen = ref(false)
const activeLink = ref('#inicio')

const links = [
  { label: 'inicio', href: '#inicio' },
  { label: 'sobre mí', href: '#sobre-mi' },
  { label: 'proyectos', href: '#proyectos' },
  { label: 'habilidades', href: '#habilidades' },
  { label: 'contacto', href: '#contacto' },
]

function closeMenu() {
  menuOpen.value = false
}

function selectLink(href: string) {
  activeLink.value = href
  closeMenu()
}
</script>

<template>
  <header class="site-header">
    <a class="brand" href="#inicio" aria-label="Ir al inicio" @click="closeMenu">
      <span class="brand-mark">&gt;_</span>
      <span>ZETH ALVAREZ</span>
    </a>

    <nav class="desktop-nav" aria-label="Navegación principal">
      <a v-for="link in links" :key="link.href" :class="{ active: activeLink === link.href }" :href="link.href" @click="selectLink(link.href)">
        [ {{ link.label }} ]
      </a>
    </nav>

    <div class="header-tools">

      <button
        class="menu-toggle"
        :class="{ open: menuOpen }"
        type="button"
        :aria-expanded="menuOpen"
        aria-controls="mobile-nav"
        :aria-label="menuOpen ? 'Cerrar menú' : 'Abrir menú'"
        @click="menuOpen = !menuOpen"
      >
        <span></span><span></span><span></span>
      </button>
    </div>

    <nav id="mobile-nav" class="mobile-nav" :class="{ open: menuOpen }" aria-label="Navegación móvil">
      <a v-for="link in links" :key="link.href" :class="{ active: activeLink === link.href }" :href="link.href" @click="selectLink(link.href)">
        <span class="selection-marker" aria-hidden="true">{{ activeLink === link.href ? '>' : '\u00a0' }}</span>
        <span>[ {{ link.label }} ]</span>
      </a>
    </nav>
  </header>
</template>

<style scoped>
.site-header {
  --ink: #16131d;
  --purple: #8257f6;
  --soft-purple: #eee9ff;
  align-items: center;
  background: #fff;
  border-top: 3px solid var(--ink);
  box-sizing: border-box;
  color: var(--ink);
  display: flex;
  font-family: "Courier New", ui-monospace, monospace;
  justify-content: space-between;
  letter-spacing: .025em;
  min-height: 68px;
  padding: 0 7.2vw;
  position: sticky;
  top: 0;
  z-index: 100;
}

.site-header a,
.site-header button {
  -webkit-tap-highlight-color: transparent;
}

.brand { align-items: center; color: inherit; display: flex; font-size: 1.125rem; font-weight: 800; gap: .65rem; text-decoration: none; white-space: nowrap; z-index: 1; }
.brand-mark { color: var(--ink); font-size: 1.25rem; letter-spacing: -.18em; }
.desktop-nav { display: flex; gap: 1.7rem; white-space: nowrap; z-index: 1; }
.desktop-nav a, .mobile-nav a { color: var(--ink); font-size: .78rem; font-weight: 700; text-decoration: none; transition: color .2s ease; }
.desktop-nav a:hover, .desktop-nav a.active, .mobile-nav a.active { color: var(--purple); }
.header-tools { align-items: center; display: flex; gap: .72rem; z-index: 1; }
.icon-button, .menu-toggle { background: transparent; border: 0; color: var(--ink); cursor: pointer; display: grid; padding: .28rem; place-items: center; }
.theme-button svg { fill: none; height: 18px; stroke: currentColor; stroke-linecap: round; stroke-width: 1.7; width: 18px; }
.grid-button { display: grid; gap: 2px; grid-template-columns: repeat(2, 5px); }
.grid-button span { background: currentColor; height: 5px; width: 5px; }
.menu-toggle { display: none; height: 36px; position: relative; width: 36px; }
.menu-toggle span { background: currentColor; display: block; height: 2px; left: 7px; position: absolute; transition: opacity .2s ease, transform .25s ease, top .25s ease; width: 22px; }
.menu-toggle span:nth-child(1) { top: 10px; }
.menu-toggle span:nth-child(2) { top: 17px; }
.menu-toggle span:nth-child(3) { top: 24px; }
.menu-toggle.open span:nth-child(1) { top: 17px; transform: rotate(45deg); }
.menu-toggle.open span:nth-child(2) { opacity: 0; transform: scaleX(0); }
.menu-toggle.open span:nth-child(3) { top: 17px; transform: rotate(-45deg); }
.mobile-nav { display: none; }
.mobile-nav a { align-items: center; display: flex; gap: .55ch; }
.selection-marker { flex: 0 0 1ch; text-align: center; }

@media (max-width: 1100px) {
  .site-header { padding: 0 6vw; }
  .desktop-nav { display: none; }
  .menu-toggle { display: grid; }
  .mobile-nav { background: #fff; box-sizing: border-box; display: grid; gap: 1.1rem; left: 0; opacity: 0; padding: 1.5rem 6vw; pointer-events: none; position: absolute; top: 100%; transform: translateY(-8px); transition: opacity .2s ease, transform .2s ease; width: 100%; z-index: 10; }
  .mobile-nav.open { opacity: 1; pointer-events: auto; transform: translateY(0); }
}

@media (max-width: 440px) {
  .site-header { min-height: 61px; }
  .brand { font-size: 1rem; gap: .45rem; }
  .theme-button, .grid-button { display: none; }
}
</style>
