# Physical device matrix

Statuses describe the last user-confirmed behavior before the Vue migration. Automated tests prove parsers and fixtures; they do not replace a physical-device test.

| Device/family | Status | Frozen evidence and caveats |
| --- | --- | --- |
| Pendulum X | Verified end-to-end | Detection, weighted battle, physical result and web result were reported working correctly. 26 captures; 25 complete. |
| Pendulum Ver.20th | Verified with caveat | Battle and Digimon detection work. There were intermittent short packets and one isolated result mismatch; later repetitions of the same matchup agreed. Preserve all partial captures for regression tests. |
| Digimon Xros Wars Mini | Verified with caveat | Battle works and the physical Digimon was corrected to `Greymon (2010 Anime Version)`. Winner must be read from the physical HitMe/result field, not assumed from the requested roll. |
| Digivice Ver. Complete | Battle verified; identity limited | Battle completes. Identity is based on locally observed candidates because there is no complete verified global mapping for this device. Do not invent an exact species from a classic slot. |
| Digital Monster Color | Verified with caveat | Physical battle and catalog mask work. The web must decode the device result; only 2 frozen DMC captures are marked `resultado_confirmado`, so this path needs extra hardware regression coverage. |
| Digital Monster X — XA | Verified end-to-end | Physical identity and winner decoding were reported correct after fixes. The DMX may hide identity with index zero; that case must remain generic. |
| Digital Monster X — XB | Verified with visual caveat | The later battle/result path worked and identified BeelStarmon X. Image/name aliases and highlighting a winner on the right are mandatory UI regressions to check. |
| Digimon Mini | Verified end-to-end | The final v12 capture identifies Koromon and confirms the physical result. The Mini remains a separate UI option even though it shares the three-pin X transport. |
| Pendulum Color | Pending physical test | Protocol/profile exists, but the available device was still in a non-combatant baby stage. Do not label verified. |
| Digimon Accel | Pending physical test | Three-pin X-compatible profile exists, but the available device was still in a non-combatant baby stage. Do not label verified. |
| Digital Monster Ver.20th | Untested | Profile exists in code; no user-confirmed physical Alpha battle is frozen. |
| Pendulum Z | Untested | Profile exists in code; no user-confirmed physical Alpha battle is frozen. |
| Digital Monster original | Untested | Classic profile exists; versions require explicit physical version information. |
| Pendulum original | Untested | Profile/catalog exists; shared slots can produce multiple candidates. |
| Monster Hunter / Godzilla / Xros Wars Color variants | Untested | Code and catalog profiles exist, but they have not been validated with the corresponding physical hardware. |
| Pendulum Color Godzilla | Untested | Catalog/profile exists; it is not part of the confirmed hardware set. |

## Behavior that must remain true

- The physical Digimon is read from the V-Pet; it is never manually selected in the interface.
- The web-selected Digimon is a visual fighter and may use a compatible protocol mask.
- No arbitrary battle packets are generated. Responses come from verified protocol profiles.
- The physical result overrides the requested/probabilistic decision when the protocol reports a different real result.
- In-Training I and II have only a 5% chance against combat-capable stages; baby stages do not battle.
- A right-side winner receives the same visible yellow highlight as a left-side winner.
- Reference Book aliases, images and attacks remain visible for both fighters.
- Mini and Xros Mini remain distinct device choices.

## Historical failures retained as regression cases

- Web winner disagreed with the physical V-Pet.
- DMX XA/XB identity or image was missing.
- Xros Mini was initially shown as Shoutmon or normal Greymon instead of the 2010 version.
- Pendulum 20th produced short/intermittent packets.
- DMC completed physically without displaying a web result.
- The winner card on the right did not receive the yellow highlight.
- Reference Book images failed through a remote tunnel.
- Mobile WebUSB reached the Beta Link but the battle request returned HTTP 502.
