// Run with the frontend/backend running and Playwright installed or in NODE_PATH.
// VPET_TEST_URL optionally overrides http://127.0.0.1:5175/vpet/.
import assert from 'node:assert/strict'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const { chromium } = require('playwright')
const browser = await chromium.launch({ headless: true, channel: 'chrome' })
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
  await page.goto(process.env.VPET_TEST_URL || 'http://127.0.0.1:5175/vpet/')
  const webCard = page.locator('.web-fighter')
  const search = page.getByPlaceholder('Buscar Digimon o Appmon')
  async function select(name) {
    await search.fill(name)
    await page.locator('.search-results button').filter({ has: page.getByText(name, { exact: true }) }).click()
    await page.waitForFunction(() => {
      const image = document.querySelector('.web-fighter img')
      return image?.complete && image.naturalWidth > 0
    })
  }

  for (const [name, filename] of [
    ['Ceresmon', 'ceresmon_2.jpg'],
    ['Bacchusmon', 'bacchusmon_2.jpg'],
    ['Beelzemon', 'beelzebumon_2.jpg'],
  ]) {
    await select(name)
    const stats = await webCard.locator('.stat-grid').innerText()
    const attacks = await webCard.locator('.attacks').innerText()
    await webCard.getByRole('button', { name: `Ilustración siguiente de ${name}` }).click()
    await page.waitForFunction(expected => {
      const image = document.querySelector('.web-fighter img')
      return image?.src.endsWith(expected) && image.complete && image.naturalWidth > 0
    }, filename)
    assert.equal((await webCard.locator('.illustration-controls small').innerText()).trim(), '2 / 2')
    assert.equal(await webCard.locator('.stat-grid').innerText(), stats)
    assert.equal(await webCard.locator('.attacks').innerText(), attacks)
    await webCard.getByRole('button', { name: `Ilustración siguiente de ${name}` }).click()
    assert.equal((await webCard.locator('.illustration-controls small').innerText()).trim(), '1 / 2')
    console.log(`${name}: segunda ilustración, ciclo y datos de batalla OK`)
  }

  await select('Agumon')
  assert.equal(await webCard.locator('.illustration-controls').count(), 0)
  console.log('Perfil con una imagen: selector oculto OK')

  await page.setViewportSize({ width: 390, height: 844 })
  await select('Ceresmon')
  const next = webCard.getByRole('button', { name: 'Ilustración siguiente de Ceresmon' })
  await next.click()
  await page.waitForFunction(() => document.querySelector('.web-fighter img')?.src.endsWith('ceresmon_2.jpg'))
  const bounds = await next.boundingBox()
  assert(bounds && bounds.width >= 44 && bounds.height >= 44)
  assert(bounds.x >= 0 && bounds.x + bounds.width <= 390)
  console.log('Móvil: selector visible y botones de 44 px OK')

  await select('Bacchusmon')
  await page.route('**/api/vpet/images/ceresmon_2.jpg', route => route.abort())
  await select('Ceresmon')
  await webCard.getByRole('button', { name: 'Ilustración siguiente de Ceresmon' }).click()
  await webCard.getByRole('status').waitFor()
  assert((await webCard.locator('img').getAttribute('src')).endsWith('/ceresmon.jpg'))
  console.log('Fallo de imagen adicional: vuelve a la principal OK')
} finally {
  await browser.close()
}
