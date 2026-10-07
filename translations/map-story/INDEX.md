# Map/Story Translation Manifest Index

Checkpoint: **4,361 / 4,361 map/story strings complete (100%)**

This index is the canonical inventory for committed map/story translation manifests. The compressed `sootopolis.vi.json.gz` is a duplicate convenience artifact and is **not** counted separately.

| Manifest | Complete strings |
|---|---:|
| `early-game-littleroot-route101-oldale.vi.json` | 146 |
| `route102-petalburg.vi.json` | 112 |
| `route103-route104-petalburgwoods.vi.json` | 81 |
| `sootopolis.vi.json` | 155 |
| `rustboro-city.vi.json` | 177 |
| `route116-rusturf-tunnel.vi.json` | 38 |
| `dewford-route106-granite-cave.vi.json` | 103 |
| `route109-slateport.vi.json` | 257 |
| `route110-mauville.vi.json` | 178 |
| `route110-trick-house.vi.json` | 146 |
| `route117-verdanturf.vi.json` | 55 |
| `route111-route112.vi.json` | 51 |
| `mtchimney-jaggedpass-lavaridge.vi.json` | 159 |
| `route113-fallarbor-route114-meteorfalls.vi.json` | 119 |
| `route115-route118-route119-weather-institute.vi.json` | 66 |
| `fortree-city.vi.json` | 78 |
| `route120-route121-mtpyre.vi.json` | 92 |
| `lilycove-core.vi.json` | 107 |
| `lilycove-contest.vi.json` | 53 |
| `lilycove-department-store.vi.json` | 29 |
| `lilycove-museum.vi.json` | 43 |
| `lilycove-trainer-fan-club.vi.json` | 38 |
| `route123.vi.json` | 6 |
| `aqua-hideout.vi.json` | 34 |
| `mossdeep-core.vi.json` | 52 |
| `mossdeep-gym.vi.json` | 52 |
| `mossdeep-space-center-steven.vi.json` | 65 |
| `route124-131-shoal-seafloor-skypillar.vi.json` | 63 |
| `pacifidlog-route132-134.vi.json` | 34 |
| `victory-road.vi.json` | 54 |
| `ever-grande-pokemon-league.vi.json` | 36 |
| `new-mauville-abandoned-ship.vi.json` | 62 |
| `magma-hideout.vi.json` | 56 |
| `battle-frontier-arena.vi.json` | 66 |
| `battle-frontier-dome.vi.json` | 113 |
| `battle-frontier-factory.vi.json` | 95 |
| `battle-frontier-palace.vi.json` | 67 |
| `battle-frontier-pike.vi.json` | 97 |
| `battle-frontier-pyramid.vi.json` | 81 |
| `battle-frontier-pyramid-dynamic.vi.json` | 128 |
| `battle-frontier-tower.vi.json` | 112 |
| `battle-frontier-exchange-lounges.vi.json` | 87 |
| `battle-frontier-outside-mart.vi.json` | 72 |
| `battle-frontier-services-scott.vi.json` | 60 |
| `optional-legendary-islands.vi.json` | 1 |
| `trainer-hill.vi.json` | 27 |
| `ss-tidal.vi.json` | 48 |
| `route105-desert-mirage.vi.json` | 8 |
| `cave-of-origin.vi.json` | 6 |
| `battle-frontier-exchange-final.vi.json` | 26 |
| `battle-frontier-lounge7-final.vi.json` | 20 |
| `battle-frontier-lounge5-final.vi.json` | 28 |
| `battle-frontier-lounge2-final.vi.json` | 35 |
| `battle-frontier-lounge3-final.vi.json` | 41 |
| `map-story-final-misc.vi.json` | 5 |
| `battle-frontier-multi-partners-regular.vi.json` | 250 |
| `battle-frontier-multi-partners-apprentices.vi.json` | 91 |
| **TOTAL** | **4,361** |

## Integrity audit — 2026-10-07

Two manifests were discovered to have been committed earlier as a 155-byte file containing a file-reference error message instead of JSON:

- `route103-route104-petalburgwoods.vi.json`
- `route110-mauville.vi.json`

Both were restored from their preserved Library copies and rechecked on `main`:

- Route 103 / Route 104 / Petalburg Woods: **81 translations**
- Route 110 / Mauville: **178 translations**

A repository-wide search after repair found **no remaining occurrence** of the bad file-reference error text.

## Map/story catalog complete — 2026-10-07

The authoritative source catalog contains **4,361 map/story strings**, and every one is now represented by a committed canonical Vietnamese manifest in this index.

Final 585-string closeout:
- Trainer Hill: **27**
- S.S. Tidal: **48**
- Route 105 / Desert Underpass / Mirage Tower fossils: **8**
- Cave of Origin / Wallace: **6**
- remaining Battle Frontier Exchange/Lounges: **150**
- final misc map/story strings: **5**
- Battle Tower Multi Partner Room: **341** (**250** regular partner strings + **91** apprentice/shared strings)

The workflow audit introduced in `tools/audit_remaining_map_story.py` reduced the remaining set from **585 → 91** after the regular partner batch; the final 91-label apprentice manifest matches that exact authoritative remainder.

**Next phase is integration, not more map/story translation:** apply the completed manifests to the v0.4 baseline using shipping-verified source/reference provenance, then continue with remaining system/UI/Arena-only categories and ROM QA. Do not screenshot-patch or mass-repoint.
