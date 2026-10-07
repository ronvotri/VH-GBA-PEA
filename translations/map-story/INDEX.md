# Map/Story Translation Manifest Index

Checkpoint: **3,139 / 4,361 map/story strings complete (~72.0%)**

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
| `optional-legendary-islands.vi.json` | 1 |
| **TOTAL** | **3,139** |

## Integrity audit — 2026-10-07

Two manifests were discovered to have been committed earlier as a 155-byte file containing a file-reference error message instead of JSON:

- `route103-route104-petalburgwoods.vi.json`
- `route110-mauville.vi.json`

Both were restored from their preserved Library copies and rechecked on `main`:

- Route 103 / Route 104 / Petalburg Woods: **81 translations**
- Route 110 / Mauville: **178 translations**

A repository-wide search after repair found **no remaining occurrence** of the bad file-reference error text.

## Next translation block

Main-story coverage through **Pokémon League / Hall of Fame** is represented by committed QA-clean manifests. Battle Arena, Dome, Factory and Palace are also QA-clean.

Next Battle Frontier facilities already inventoried:
- Battle Pike: **97 map-local strings**
- Battle Pyramid: **81**
- Battle Tower: **112**
- subtotal: **290**

After those, continue remaining Battle Frontier shared lounges/services and any post-game map/story gaps not yet represented in this index.

Project rules remain unchanged: **v0.4 baseline, no screenshot-by-screenshot patching, no mass-repoint.**
