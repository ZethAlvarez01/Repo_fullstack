const WCH_VENDOR_ID = 0x1a86
const SUPPORTED_PRODUCT_IDS = new Set([0x7523, 0x5523])
const CH343_PRODUCT_ID = 0x55d3
const CH341_BAUD_BASE_FACTOR = 1532620800
const CH341_BAUD_BASE_DIV_MAX = 3
const CH340_INIT = 0xa1
const CH340_SET_BAUDRATE = 0x9a
const CH340_SET_HANDSHAKE = 0xa4
const VENDOR_CLASS = 0xff
const MAX_TRANSFER_SIZE = 64

type UsbDevice = any
type UsbApi = {
  requestDevice(options: { filters: { vendorId: number }[] }): Promise<UsbDevice>
  addEventListener(type: 'disconnect', listener: (event: any) => void): void
  removeEventListener(type: 'disconnect', listener: (event: any) => void): void
}
type SerialApi = { requestPort(options: { filters: { usbVendorId: number }[] }): Promise<any> }

function usbApi(): UsbApi | undefined {
  return (navigator as Navigator & { usb?: UsbApi }).usb
}

function serialApi(): SerialApi | undefined {
  return (navigator as Navigator & { serial?: SerialApi }).serial
}

function assertTransfer(result: { status: string }, action: string) {
  if (result.status !== 'ok') throw new Error(`CH340: falló ${action} (${result.status}).`)
}

function wait(milliseconds: number) {
  return new Promise(resolve => setTimeout(resolve, milliseconds))
}

export interface Ch340Info {
  vendorId: number
  productId: number
  label: string
}

export class Ch340Transport {
  private readonly onData: (data: Uint8Array) => void
  private readonly onStateChange?: (connected: boolean) => void
  private device: UsbDevice | null = null
  private serialPort: any = null
  private serialReader: any = null
  private serialWriter: any = null
  private interfaceNumber: number | null = null
  private endpointIn: number | null = null
  private endpointOut: number | null = null
  private reading = false
  private readTask: Promise<void> | null = null
  private writeChain: Promise<void> = Promise.resolve()
  private readonly onDisconnect = (event: any) => {
    if (event.device === this.device) void this.disconnect()
  }

  constructor(onData: (data: Uint8Array) => void, onStateChange?: (connected: boolean) => void) {
    this.onData = onData
    this.onStateChange = onStateChange
  }

  static supported() {
    return Boolean(usbApi() || serialApi())
  }

  get connected() {
    return Boolean((this.device?.opened || this.serialPort?.readable) && this.reading)
  }

  async connect(): Promise<Ch340Info> {
    if (!window.isSecureContext) throw new Error('El Beta Link requiere HTTPS o localhost.')
    if (/Windows/i.test(navigator.userAgent) && serialApi()) return this.connectSerial()
    const usb = usbApi()
    if (!usb) throw new Error('Este navegador no admite WebUSB. Usa Chrome o Edge.')
    if (this.connected && this.device) return this.info(this.device)

    const device = await usb.requestDevice({ filters: [{ vendorId: WCH_VENDOR_ID }] })
    if (device.productId === CH343_PRODUCT_ID) throw new Error('El CH343 requiere Web Serial; este Beta Link usa CH340.')
    if (!SUPPORTED_PRODUCT_IDS.has(device.productId)) throw new Error('El dispositivo seleccionado no es un CH340 compatible.')

    try {
      try {
        await device.open()
      } catch (cause) {
        const detail = cause instanceof Error ? cause.message : String(cause)
        if (/access denied/i.test(detail)) {
          throw new Error('Windows negó el acceso al Beta Link. Cierra Python, Arduino IDE y cualquier monitor que esté usando su puerto COM; después desconéctalo, vuelve a conectarlo e inténtalo otra vez.')
        }
        throw cause
      }
      if (!device.configuration || device.configuration.configurationValue !== 1) await device.selectConfiguration(1)
      this.device = device
      this.findBulkInterface(device)
      if (this.interfaceNumber === null || this.endpointIn === null || this.endpointOut === null) {
        throw new Error('No se encontró la interfaz de datos del CH340.')
      }
      await device.claimInterface(this.interfaceNumber)
      await this.vendorOut(CH340_INIT, 0, 0)
      await this.setBaudRate(9600)
      await this.setSignals(false, false)
      this.reading = true
      usb.addEventListener('disconnect', this.onDisconnect)
      this.readTask = this.readLoop()
      this.onStateChange?.(true)
      return this.info(device)
    } catch (cause) {
      await this.disconnect()
      throw cause
    }
  }

  async disconnect() {
    this.reading = false
    usbApi()?.removeEventListener('disconnect', this.onDisconnect)
    if (this.serialReader) {
      try { await this.serialReader.cancel() } catch { /* Already disconnected. */ }
    }
    if (this.device?.opened) {
      if (this.interfaceNumber !== null) {
        try { await this.device.releaseInterface(this.interfaceNumber) } catch { /* Already released. */ }
      }
      try { await this.device.close() } catch { /* Already closed. */ }
    }
    if (this.readTask) {
      try { await this.readTask } catch { /* The cable may already be gone. */ }
      this.readTask = null
    }
    if (this.serialReader) {
      try { this.serialReader.releaseLock() } catch { /* Already released. */ }
      this.serialReader = null
    }
    if (this.serialWriter) {
      try { this.serialWriter.releaseLock() } catch { /* Already released. */ }
      this.serialWriter = null
    }
    if (this.serialPort) {
      try { await this.serialPort.close() } catch { /* Already closed. */ }
      this.serialPort = null
    }
    this.device = null
    this.interfaceNumber = null
    this.endpointIn = null
    this.endpointOut = null
    this.onStateChange?.(false)
  }

  write(data: Uint8Array | string) {
    const bytes = typeof data === 'string' ? new TextEncoder().encode(data) : data
    const run = this.writeChain.then(async () => {
      if (this.serialWriter) {
        await this.serialWriter.write(bytes)
        return
      }
      if (!this.device?.opened || this.endpointOut === null) throw new Error('El Beta Link no está conectado.')
      for (let offset = 0; offset < bytes.length; offset += MAX_TRANSFER_SIZE) {
        const result = await this.device.transferOut(this.endpointOut, bytes.slice(offset, offset + MAX_TRANSFER_SIZE))
        assertTransfer(result, 'la escritura USB')
      }
    })
    this.writeChain = run.catch(() => undefined)
    return run
  }

  private async connectSerial(): Promise<Ch340Info> {
    const serial = serialApi()
    if (!serial) throw new Error('Web Serial no está disponible en este navegador.')
    const port = await serial.requestPort({ filters: [{ usbVendorId: WCH_VENDOR_ID }] })
    const rawInfo = port.getInfo?.() ?? {}
    const vendorId = rawInfo.usbVendorId ?? WCH_VENDOR_ID
    const productId = rawInfo.usbProductId ?? 0
    if (productId && !SUPPORTED_PRODUCT_IDS.has(productId)) throw new Error('El puerto seleccionado no pertenece al Beta Link CH340.')
    try {
      await port.open({ baudRate: 9600, dataBits: 8, stopBits: 1, parity: 'none', flowControl: 'none' })
      this.serialPort = port
      this.serialReader = port.readable.getReader()
      this.serialWriter = port.writable.getWriter()
      this.reading = true
      this.readTask = this.readSerialLoop()
      this.onStateChange?.(true)
      return { vendorId, productId, label: productId ? `CH340 COM ${vendorId.toString(16)}:${productId.toString(16)}` : 'CH340 COM' }
    } catch (cause) {
      this.serialPort = port
      await this.disconnect()
      const detail = cause instanceof Error ? cause.message : String(cause)
      if (/failed to open|access denied|already open/i.test(detail)) throw new Error('Windows no pudo abrir el puerto COM. Cierra cualquier programa que esté usando el Beta Link y vuelve a intentar.')
      throw cause
    }
  }

  private async readSerialLoop() {
    while (this.reading && this.serialReader) {
      const { value, done } = await this.serialReader.read()
      if (done) break
      if (value?.byteLength) this.onData(value)
    }
  }

  private info(device: UsbDevice): Ch340Info {
    return { vendorId: device.vendorId, productId: device.productId, label: `CH340 ${device.vendorId.toString(16)}:${device.productId.toString(16)}` }
  }

  private findBulkInterface(device: UsbDevice) {
    for (const iface of device.configuration?.interfaces ?? []) {
      for (const alternate of iface.alternates) {
        if (alternate.interfaceClass !== VENDOR_CLASS) continue
        const endpointIn = alternate.endpoints.find((endpoint: any) => endpoint.type === 'bulk' && endpoint.direction === 'in')
        const endpointOut = alternate.endpoints.find((endpoint: any) => endpoint.type === 'bulk' && endpoint.direction === 'out')
        if (endpointIn && endpointOut) {
          this.interfaceNumber = iface.interfaceNumber
          this.endpointIn = endpointIn.endpointNumber
          this.endpointOut = endpointOut.endpointNumber
          return
        }
      }
    }
  }

  private async vendorOut(request: number, value: number, index: number) {
    if (!this.device?.opened) throw new Error('El CH340 no está abierto.')
    const result = await this.device.controlTransferOut({ requestType: 'vendor', recipient: 'device', request, value, index })
    assertTransfer(result, `el comando 0x${request.toString(16)}`)
  }

  private async setBaudRate(baudRate: number) {
    let factor = Math.floor(CH341_BAUD_BASE_FACTOR / baudRate)
    let divisor = CH341_BAUD_BASE_DIV_MAX
    while (factor > 0xfff0 && divisor > 0) { factor >>= 3; divisor-- }
    if (factor > 0xfff0) throw new Error(`Velocidad ${baudRate} no compatible.`)
    factor = 0x10000 - factor
    await this.vendorOut(CH340_SET_BAUDRATE, 0x1312, (factor & 0xff00) | divisor)
    await this.vendorOut(CH340_SET_BAUDRATE, 0x0f2c, factor & 0xff)
    await wait(50)
  }

  private async setSignals(dtr: boolean, rts: boolean) {
    const value = ~((dtr ? 1 << 5 : 0) | (rts ? 1 << 6 : 0)) & 0xffff
    await this.vendorOut(CH340_SET_HANDSHAKE, value, 0)
  }

  private async readLoop() {
    while (this.reading && this.device?.opened && this.endpointIn !== null) {
      try {
        const result = await this.device.transferIn(this.endpointIn, MAX_TRANSFER_SIZE)
        if (result.status === 'stall') {
          await this.device.clearHalt('in', this.endpointIn)
        } else if (result.status === 'ok' && result.data?.byteLength) {
          this.onData(new Uint8Array(result.data.buffer, result.data.byteOffset, result.data.byteLength))
        }
      } catch (cause) {
        if (this.reading) throw cause
      }
    }
  }
}
