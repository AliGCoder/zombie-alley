# Zombie Alley

A browser zombie shooter built with [three.js](https://threejs.org). 28 Days Later–style infected sprint at you down a London street, at night in the rain, by day, or on Google's real 3D scan of Oxford Street.

**Play online:** https://aligcoder.github.io/zombie-alley/

## Games

| File | What it is |
|---|---|
| `zombie-arcade.html` | **Zombie Alley Arcade**, the main game: rail shooter with real 3D models |
| `zombie-waves-3d.html` | Earlier first-person wave survival |
| `zombie-waves.html` | The original 2D wave game |

## Controls

- **Mouse:** aim · **Click:** shoot · **Right-click / Space / R:** reload
- Headshots kill instantly; chain hits for combos
- Shoot pickups: first-aid box = life, ammo box = machine gun, crate = shotgun, grenade = bomb
- Don't shoot the survivors
- **T** (title screen): switch level: Night · Day (London) · Live London
- **K** (title screen): enter your Google Maps API key for Live London
- **P** pause · **M** mute · **G** graphics quality

## Run it locally

The models load over HTTP, so use the tiny included server (needs [Node.js](https://nodejs.org)):

```
node serve.js
```

Then open http://localhost:8080

## Live London (optional)

The Live London level streams Google's Photorealistic 3D Tiles. Create a key in Google Cloud Console with the **Map Tiles API** enabled, then press **K** on the title screen and paste it. The key is stored only in your browser's local storage and is never part of this repository. Restrict the key to the sites you play on (for example `https://aligcoder.github.io/*` and `http://localhost:8080/*`).

## Credits & licences

| Asset | Author | Licence |
|---|---|---|
| Zombie model (`models/zombie.glb`) | [patromes](https://sketchfab.com/patromes) on Sketchfab | CC BY 4.0 |
| First-person arms & pistol (`assets/fps_arms`) | "FPS pistol animations" by [Cransh](https://sketchfab.com/ccransh): arms by bumstrum, pistol (Springfield XD Mod.2) by raimeiyonke | CC BY 4.0 |
| Buildings, street props, pistol, pickups, barrels, textures, Bethnal Green HDRI | [Poly Haven](https://polyhaven.com) | CC0 |
| Soldier survivor (`assets/Soldier.glb`) | three.js examples (Mixamo character) | see three.js repository |
| Live London 3D city | Google Photorealistic 3D Tiles (streamed, not stored) | Google Maps Platform terms |
| Engine | [three.js](https://threejs.org) r165, [3d-tiles-renderer](https://github.com/NASA-AMMOS/3DTilesRendererJS) | MIT / Apache-2.0 |

The large zombie model is stored with Git LFS.
