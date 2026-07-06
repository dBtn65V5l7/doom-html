# DOOM in einer HTML-Datei

`index.html` ist das komplette Spiel: **DOOM (1993, id Software)** als eine
einzige, offline lauffähige Datei. Doppelklick genügt — läuft direkt von
`file://` in jedem modernen Browser (Chrome, Edge, Firefox), ohne Server,
ohne Internet, ohne Installation, ohne Admin-Rechte.

## Was steckt drin

- **Engine:** Der originale id-Software-DOOM-Quellcode (GPLv2) über die
  Portierungsschicht [doomgeneric](https://github.com/ozkl/doomgeneric),
  mit Emscripten zu WebAssembly kompiliert. Das WASM-Binärmodul ist als
  Base64 in die HTML eingebettet.
- **Spieldaten:** `DOOM1.WAD` v1.9 — die offizielle Shareware-Episode 1
  „Knee-Deep in the Dead" (MD5 `f0cefca49926d00903cf57551d901abe`),
  ebenfalls als Base64 eingebettet. Die Shareware-WAD darf laut id Software
  frei weiterverteilt werden.
- Kein `fetch`, kein CDN, kein SharedArrayBuffer, keine COOP/COEP-Header.

## Steuerung (klassisch)

| Taste | Funktion |
|---|---|
| Pfeiltasten | Laufen / Drehen |
| Strg | Schießen |
| Leertaste | Tür / Schalter |
| Alt + Pfeile | Seitwärts (Strafe) |
| Shift | Rennen |
| 1–7 | Waffe wählen |
| Esc / Enter | Menü |
| Tab | Karte |
| F2 / F3 | Speichern / Laden |

## Vollversion

Wer die Vollversion (`DOOM.WAD`) besitzt: den Base64-Inhalt des Blocks
`<script id="wad-data">` in `index.html` durch `base64(DOOM.WAD)` ersetzen
(unter Windows: `certutil -encode DOOM.WAD wad.b64`, Kopf-/Fußzeile
entfernen). Die Engine erkennt die Version automatisch.

## Selbst bauen

Siehe `build/`:

1. `doomgeneric_emscripten.c` — SDL-freies Plattform-Backend
   (Canvas-Rendering, Tastatur-Queue, 35-fps-Mainloop) nach
   `doomgeneric/doomgeneric/` kopieren.
2. `build.sh` — kompiliert mit `emcc` zu `doom.js` + `doom.wasm`.
3. `gen_html.py` — bettet Engine, WASM und WAD als Base64 in `index.html`.

Engine-Quellcode: GPLv2 (id Software, Simon Howard/Chocolate Doom, ozkl/doomgeneric).

## Hinweis

Kein Sound (das Backend implementiert nur Grafik + Eingabe). Spielstände
(F2) leben im Arbeitsspeicher der Seite und überleben kein Neuladen.
