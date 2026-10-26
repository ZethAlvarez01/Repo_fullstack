# Vue V-Pet interface

Migration step 3 replaces the temporary `/vpet/` page with an independent Vue entry point.

## Entry points

- `/` uses `frontend/src/main.ts` and keeps the existing portfolio.
- `/vpet/` uses `frontend/src/vpet-main.ts` and mounts `VPetApp.vue`.

Vite builds both pages. During development, `/api` is proxied to FastAPI on `127.0.0.1:8000`.

## Implemented

- Atlas-first Reference Book search with generated JSON fallback.
- R2 images through `/api/vpet/images/{filename}`.
- Web rival selector and full profile card.
- Physical V-Pet family selector; the physical species remains automatic.
- Probability calculator using the canonical configuration.
- Live browser geolocation panel.
- Serial-console presentation and general reset.
- Responsive desktop/mobile layout.
- Direct CH340 WebUSB connection at 9600 baud from Vue.
- Live firmware serial output and clean USB disconnect/reset lifecycle.

## Deliberately pending

Migration step 4 transport is in place. The remaining work is the local battle state machine: arm the selected family, identify the physical V-Pet from the firmware query, make the weighted decision and parse the physical result. No remote API call is placed in the time-critical V-Pet exchange.
