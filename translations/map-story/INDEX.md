# Map/Story Translation Manifest Index

Checkpoint: **2,492 / 4,361 map/story strings complete (~57.1%)**

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
| **TOTAL** | **2,492** |

## Integrity audit — 2026-10-07

Two manifests were discovered to have been committed earlier as a 155-byte file containing a file-reference error message instead of JSON:

- `route103-route104-petalburgwoods.vi.json`
- `route110-mauville.vi.json`

Both were restored from their preserved Library copies and rechecked on `main`:

- Route 103 / Route 104 / Petalburg Woods: **81 translations**
- Route 110 / Mauville: **178 translations**

A repository-wide search after repair found **no remaining occurrence** of the bad file-reference error text.

## Next translation block

Route 122 / Safari Zone have no map-local `.string` entries in this source scope. Route 123 is complete.

Aqua Hideout is **34 / 34** complete.
Mossdeep is **169 / 169** complete across core + Gym + Space Center / Steven.

Continue with the next story-heavy block after Mossdeep:
- Route 124 / Route 125 / Shoal Cave
- Route 126 / Route 127 / Route 128
- Seafloor Cavern
- Route 129 / Route 130 / Route 131 / Sky Pillar
- remaining late-game / post-game map-story gaps

Project rules remain unchanged: **v0.4 baseline, no screenshot-by-screenshot patching, no mass-repoint.**
