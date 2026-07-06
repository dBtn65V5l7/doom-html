# 🔥 DOOM in a single HTML file

```
 ██████╗   ██████╗   ██████╗  ███╗   ███╗
 ██╔══██╗ ██╔═══██╗ ██╔═══██╗ ████╗ ████║
 ██║  ██║ ██║   ██║ ██║   ██║ ██╔████╔██║
 ██║  ██║ ██║   ██║ ██║   ██║ ██║╚██╔╝██║
 ██████╔╝ ╚██████╔╝ ╚██████╔╝ ██║ ╚═╝ ██║
 ╚═════╝   ╚═════╝   ╚═════╝  ╚═╝     ╚═╝
        one file · offline · the real thing
```

**The real DOOM (1993, id Software) — the whole game in one `index.html`.**

No server. No internet. No installation. No admin rights.
Double-click the file → browser opens → play.

| | |
|---|---|
| 📦 **One file** | `index.html`, ~6 MB — engine, WASM and WAD embedded as base64 |
| 🖥️ **Runs anywhere** | Chrome, Edge, Firefox — straight from `file://`, even off a USB stick |
| 🚫 **Zero network** | no `fetch`, no CDN, the network tab stays empty (verified) |
| 🔓 **No special powers** | no SharedArrayBuffer, no COOP/COEP headers, no threads |
| ⚖️ **100 % legal** | GPL engine + official shareware WAD (freely redistributable) |

---

## 📸 Screenshots

| Title screen | E1M1 — Hangar |
|---|---|
| ![Title screen](assets/screenshot-title.png) | ![E1M1 gameplay](assets/screenshot-e1m1.png) |

*Screenshots taken by the automated self-test: Chromium, opened via `file://`, zero network requests.*

---

## 🚀 Quick start

1. Download `index.html` (or copy it to a USB stick)
2. Double-click it
3. Press <kbd>Enter</kbd> → **New Game** → episode → skill
4. Welcome to *Knee-Deep in the Dead*. Good luck, marine. 💀

## 🎮 Controls (classic, like 1993)

| Key | Action |
|---|---|
| <kbd>↑</kbd> <kbd>↓</kbd> | Move forward / back |
| <kbd>←</kbd> <kbd>→</kbd> | Turn |
| <kbd>Ctrl</kbd> | Fire |
| <kbd>Space</kbd> | Open door / use switch |
| <kbd>Alt</kbd> + <kbd>←</kbd> <kbd>→</kbd> | Strafe |
| <kbd>Shift</kbd> | Run |
| <kbd>1</kbd>–<kbd>7</kbd> | Select weapon |
| <kbd>Esc</kbd> / <kbd>Enter</kbd> | Menu / select |
| <kbd>Tab</kbd> | Automap |
| <kbd>F2</kbd> / <kbd>F3</kbd> | Save / load |

Just type the cheat codes — `iddqd`, `idkfa` &amp; co. work. 😈

## 🧱 How it works

```
┌──────────────────────────── index.html ────────────────────────────┐
│                                                                     │
│  <canvas>  ← 640×400, image-rendering: pixelated                    │
│                                                                     │
│  <script id="wad-data">   DOOM1.WAD v1.9 (base64, ~5.6 MB)          │
│  <script id="wasm-data">  engine binary (base64, ~500 KB)           │
│                                                                     │
│  bootstrap JS   base64 → bytes → Module.wasmBinary + MEMFS file     │
│  keyboard JS    keydown/keyup → DOOM key codes → key queue (C)      │
│  render JS      BGRA framebuffer → RGBA → putImageData()            │
│                                                                     │
│  Emscripten glue + WASM  =  original id DOOM code (GPLv2)           │
│                             via doomgeneric, main loop @ 35 fps     │
└─────────────────────────────────────────────────────────────────────┘
```

- **Engine:** the original DOOM source code that id Software released under
  the GPL, compiled to WebAssembly with Emscripten through the
  [doomgeneric](https://github.com/ozkl/doomgeneric) porting layer.
- **Backend:** a custom, SDL-free platform backend
  ([`build/doomgeneric_emscripten.c`](build/doomgeneric_emscripten.c)):
  direct canvas rendering, a keyboard ring buffer, and
  `emscripten_set_main_loop` at 35 fps — exactly DOOM's internal tic rate.
- **Game data:** `DOOM1.WAD` v1.9, the official shareware Episode 1
  (MD5 `f0cefca49926d00903cf57551d901abe`, 4,196,020 bytes).

## 💿 Using the full version

The full game (`DOOM.WAD`) is **not** included — it is commercial software
and may not be redistributed. If you own it (e.g. from the Steam/GOG
release), load it like this:

**Easiest way — the button below the canvas:**

1. Open `index.html`
2. Click **“💽 Load your own DOOM.WAD (full version)”** and pick your
   `DOOM.WAD`
3. The game restarts as the full version (*Ultimate Doom* with Episode 4
   works too). The WAD is stored locally in your browser (IndexedDB) and
   never leaves your machine. “↩ Back to shareware” undoes it.

**Alternatively, bake it in** (survives clearing browser data):

1. Encode the WAD as base64 — on Windows:
   ```bat
   certutil -encode DOOM.WAD wad.b64
   ```
   (remove the first and last `-----BEGIN/END CERTIFICATE-----` lines)
2. In `index.html`, replace the contents of the `<script id="wad-data">`
   block with the base64 text.

The engine detects the game version automatically from the WAD contents.
*Note: DOOM II (`DOOM2.WAD`) is not supported by this build — only
DOOM 1 / Ultimate Doom.*

## 🔨 Building it yourself

Requires `emscripten` and `python3`. Steps (see [`build/`](build/)):

```bash
# 1. Fetch the doomgeneric source and drop in the backend
cp build/doomgeneric_emscripten.c doomgeneric/doomgeneric/

# 2. Compile the engine  →  doom.js + doom.wasm
bash build/build.sh

# 3. Bake everything into one HTML file  →  index.html
python3 build/gen_html.py
```

## ❓ FAQ

**Why no sound?**
The backend implements video + input only. The original sound modules
depend on SDL/SDL_mixer, which was deliberately left out to keep the file
small and dependency-free. The game plays fine without it.

**Do savegames persist?**
<kbd>F2</kbd> saves live in the page's memory and do not survive a reload.
Good enough for one session.

**Is this a clone like Freedoom?**
No. Engine = original id source code (GPL). Data = original shareware WAD
by id Software. This is *the* DOOM.

## ⚖️ License

- **Engine:** GPLv2 — © id Software, Simon Howard (Chocolate Doom),
  ozkl (doomgeneric). Source and build scripts live in
  [`build/`](build/), upstream: <https://github.com/ozkl/doomgeneric>
- **DOOM1.WAD:** © id Software 1993. id Software permits free
  redistribution of the unmodified shareware version.
- *DOOM* is a trademark of id Software LLC.
