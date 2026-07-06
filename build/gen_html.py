#!/usr/bin/env python3
"""Assemble the single-file index.html: page + bootstrap JS + base64 WASM + base64 WAD + engine JS."""
import base64
import pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"

doom_js = (OUT / "doom.js").read_text()
wasm_b64 = base64.b64encode((OUT / "doom.wasm").read_bytes()).decode()
wad_b64 = base64.b64encode((HERE / "doom1.wad").read_bytes()).decode()

assert "</script" not in doom_js.lower(), "engine js would break out of script tag"

# Wrap base64 to 400-char lines so editors don't choke on one huge line.
def wrap(s, n=400):
    return "\n".join(s[i:i + n] for i in range(0, len(s), n))

html = r"""<!DOCTYPE html>
<!--
  DOOM (1993, id Software) - the whole game in a single file.

  Engine: the original id Software DOOM source code (GPLv2) via the
  "doomgeneric" porting layer (https://github.com/ozkl/doomgeneric),
  compiled to WebAssembly with Emscripten. The GPL source is freely
  available.

  Game data: DOOM1.WAD v1.9 (shareware, Episode 1 "Knee-Deep in the Dead",
  MD5 f0cefca49926d00903cf57551d901abe). id Software permits free
  redistribution of the unmodified shareware WAD.

  Runs fully offline from file:// - no server, no CDN, no fetch,
  no SharedArrayBuffer, no COOP/COEP headers required.

  FULL VERSION: if you own the full game (DOOM.WAD / Ultimate Doom),
  click "Load your own DOOM.WAD" below the canvas and pick your file.
  It is stored locally in the browser (IndexedDB) and never leaves your
  machine. Alternatively, replace the base64 content of the
  <script id="wad-data"> block below
  (Windows: certutil -encode DOOM.WAD wad.b64, strip header/footer lines).
-->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DOOM</title>
<style>
  html, body { margin: 0; padding: 0; background: #1a1a1a; color: #bbb; font-family: 'Courier New', monospace; }
  body { display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
  h1 { color: #c00; font-size: 28px; letter-spacing: 8px; margin: 16px 0 10px; text-shadow: 0 0 12px #600; }
  #screen {
    width: min(96vw, 152vh);
    max-width: 1280px;
    aspect-ratio: 8 / 5;
    background: #000;
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    border: 2px solid #333;
    box-shadow: 0 0 30px rgba(0,0,0,.8);
    outline: none;
  }
  #status { margin: 10px; font-size: 14px; color: #888; min-height: 1.2em; }
  #status.error { color: #f55; white-space: pre-wrap; }
  #wadbar { margin: 2px 0 8px; font-size: 12px; color: #777; display: flex; gap: 10px; align-items: center; }
  #wadbar button {
    background: #2a2a2a; color: #ccc; border: 1px solid #555; border-radius: 3px;
    font-family: inherit; font-size: 12px; padding: 3px 10px; cursor: pointer;
  }
  #wadbar button:hover { background: #3a3a3a; border-color: #777; }
  #wadlabel { color: #9a9; }
  #controls { font-size: 12px; color: #777; margin-bottom: 18px; text-align: center; line-height: 1.7; }
  #controls b { color: #aaa; }
  kbd { background: #2a2a2a; border: 1px solid #444; border-radius: 3px; padding: 0 5px; color: #ccc; font-family: inherit; }
</style>
</head>
<body>
<h1>DOOM</h1>
<canvas id="screen" width="640" height="400" tabindex="0"></canvas>
<div id="status">LOADING &hellip;</div>
<div id="wadbar">
  <span id="wadlabel"></span>
  <button id="wadpick" type="button">&#128189; Load your own DOOM.WAD (full version)</button>
  <button id="wadreset" type="button" hidden>&#8617; Back to shareware</button>
  <input id="wadfile" type="file" accept=".wad" hidden>
</div>
<div id="controls">
  <kbd>&uarr;</kbd><kbd>&darr;</kbd> move &nbsp; <kbd>&larr;</kbd><kbd>&rarr;</kbd> turn &nbsp;
  <kbd>Ctrl</kbd> fire &nbsp; <kbd>Space</kbd> open/use &nbsp;
  <kbd>Alt</kbd>+<kbd>&larr;</kbd><kbd>&rarr;</kbd> strafe &nbsp; <kbd>Shift</kbd> run<br>
  <kbd>1</kbd>&ndash;<kbd>7</kbd> weapons &nbsp; <kbd>Enter</kbd> select &nbsp; <kbd>Esc</kbd> menu &nbsp;
  <kbd>Tab</kbd> map &nbsp; <kbd>F2</kbd> save &nbsp; <kbd>F3</kbd> load<br>
  <b>DOOM</b> &mdash; id Software 1993 &mdash; engine GPLv2 (doomgeneric/WebAssembly)
</div>

<script id="wad-data" type="text/plain">
@WAD_B64@
</script>
<script id="wasm-data" type="text/plain">
@WASM_B64@
</script>
<script id="engine-code" type="text/plain">
@DOOM_JS@
</script>

<script>
"use strict";

function b64ToBytes(id) {
  var b64 = document.getElementById(id).textContent.replace(/[^A-Za-z0-9+/=]/g, "");
  var bin = atob(b64);
  var bytes = new Uint8Array(bin.length);
  for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

var statusEl = document.getElementById("status");
var canvas = document.getElementById("screen");
var ctx2d = null, frameImage = null, framePixels = null;

function fatal(msg) {
  statusEl.className = "error";
  statusEl.textContent = "ERROR: " + msg;
}

// ---- User-provided WAD (full version) in IndexedDB -----------------------
// The WAD picked by the user stays in this browser's local storage on this
// machine; nothing is ever uploaded.
var DB_NAME = "doom-single-file", STORE = "wad";

function idbOpen() {
  return new Promise(function (res, rej) {
    var rq = indexedDB.open(DB_NAME, 1);
    rq.onupgradeneeded = function () { rq.result.createObjectStore(STORE); };
    rq.onsuccess = function () { res(rq.result); };
    rq.onerror = function () { rej(rq.error); };
  });
}
function idbGetWad() {
  return idbOpen().then(function (db) {
    return new Promise(function (res, rej) {
      var rq = db.transaction(STORE).objectStore(STORE).get("custom");
      rq.onsuccess = function () { res(rq.result || null); };
      rq.onerror = function () { rej(rq.error); };
    });
  });
}
function idbSetWad(bytes) {
  return idbOpen().then(function (db) {
    return new Promise(function (res, rej) {
      var tx = db.transaction(STORE, "readwrite");
      tx.objectStore(STORE).put(bytes, "custom");
      tx.oncomplete = function () { res(); };
      tx.onerror = function () { rej(tx.error); };
    });
  });
}
function idbClearWad() {
  return idbOpen().then(function (db) {
    return new Promise(function (res, rej) {
      var tx = db.transaction(STORE, "readwrite");
      tx.objectStore(STORE).delete("custom");
      tx.oncomplete = function () { res(); };
      tx.onerror = function () { rej(tx.error); };
    });
  });
}

document.getElementById("wadpick").addEventListener("click", function () {
  document.getElementById("wadfile").click();
});
document.getElementById("wadfile").addEventListener("change", function () {
  var f = this.files[0];
  if (!f) return;
  var rd = new FileReader();
  rd.onload = function () {
    var bytes = new Uint8Array(rd.result);
    var magic = String.fromCharCode(bytes[0], bytes[1], bytes[2], bytes[3]);
    if (magic !== "IWAD") { fatal("Not an IWAD file (expected DOOM.WAD)."); return; }
    idbSetWad(bytes).then(function () { location.reload(); },
      function (e) { fatal("Could not store the WAD locally: " + e); });
  };
  rd.readAsArrayBuffer(f);
});
document.getElementById("wadreset").addEventListener("click", function () {
  idbClearWad().then(function () { location.reload(); });
});

// ---- DOOM key codes (doomkeys.h) -----------------------------------------
var KEY_RIGHT = 0xae, KEY_LEFT = 0xac, KEY_UP = 0xad, KEY_DOWN = 0xaf;
var KEY_FIRE = 0xa3, KEY_USE = 0xa2, KEY_RALT = 0x80 + 0x38, KEY_RSHIFT = 0x80 + 0x36;
var CODE_MAP = {
  ArrowRight: KEY_RIGHT, ArrowLeft: KEY_LEFT, ArrowUp: KEY_UP, ArrowDown: KEY_DOWN,
  ControlLeft: KEY_FIRE, ControlRight: KEY_FIRE,
  Space: KEY_USE,
  AltLeft: KEY_RALT, AltRight: KEY_RALT,
  ShiftLeft: KEY_RSHIFT, ShiftRight: KEY_RSHIFT,
  Escape: 27, Enter: 13, NumpadEnter: 13, Tab: 9, Backspace: 0x7f, Pause: 0xff,
  F1: 0x80 + 0x3b, F2: 0x80 + 0x3c, F3: 0x80 + 0x3d, F4: 0x80 + 0x3e, F5: 0x80 + 0x3f,
  F6: 0x80 + 0x40, F7: 0x80 + 0x41, F8: 0x80 + 0x42, F9: 0x80 + 0x43, F10: 0x80 + 0x44,
  F11: 0x80 + 0x57,
  Minus: 0x2d, Equal: 0x3d
};

function doomKeyFor(e) {
  var k = CODE_MAP[e.code];
  if (k !== undefined) return k;
  // Letters/digits as ASCII (weapon select, y/n prompts, cheats like IDDQD)
  if (e.key && e.key.length === 1) {
    var c = e.key.charCodeAt(0);
    if (c >= 32 && c < 127) return String.fromCharCode(c).toLowerCase().charCodeAt(0);
  }
  return undefined;
}

var engineReady = false;
function onKey(pressed, e) {
  var k = doomKeyFor(e);
  if (k === undefined) return;
  e.preventDefault();
  if (!engineReady || (pressed && e.repeat)) return;
  Module._DG_PushKeyEvent(pressed, k);
}
window.addEventListener("keydown", function (e) { onKey(1, e); });
window.addEventListener("keyup", function (e) { onKey(0, e); });
window.addEventListener("blur", function () {
  // Release all keys, or the marine keeps running after Alt+Tab.
  if (!engineReady) return;
  [KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN, KEY_FIRE, KEY_USE, KEY_RALT, KEY_RSHIFT].forEach(
    function (k) { Module._DG_PushKeyEvent(0, k); });
});

// ---- Emscripten module ----------------------------------------------------
var Module = {
  print: function (t) { console.log(t); },
  printErr: function (t) { console.warn(t); },
  wasmBinary: null,          // set in boot()
  preRun: [],                // set in boot()
  onRuntimeInitialized: function () { engineReady = true; },
  onAbort: function (what) { fatal("Engine aborted: " + what); },

  // Called from doomgeneric_emscripten.c:
  dg_init: function (w, h) {
    canvas.width = w; canvas.height = h;
    ctx2d = canvas.getContext("2d");
    frameImage = ctx2d.createImageData(w, h);
    framePixels = new Uint32Array(frameImage.data.buffer);
    statusEl.textContent = "";
    canvas.focus();
  },
  dg_drawFrame: function (ptr, w, h) {
    // Engine buffer: BGRA bytes => LE uint32 0xAARRGGBB.
    // Canvas buffer: RGBA bytes => LE uint32 0xAABBGGRR.
    var heap = Module.HEAPU32, off = ptr >> 2, n = w * h, out = framePixels;
    for (var i = 0; i < n; i++) {
      var px = heap[off + i];
      out[i] = 0xff000000 | ((px & 0xff) << 16) | (px & 0xff00) | ((px >>> 16) & 0xff);
    }
    ctx2d.putImageData(frameImage, 0, 0);
  },
  dg_setTitle: function (t) { document.title = t; }
};

window.onerror = function (msg) { if (!engineReady) fatal(String(msg)); };

// ---- Boot: resolve the WAD source first, then inject the engine ----------
function boot(customWad) {
  var wadBytes, label;
  if (customWad) {
    wadBytes = customWad;
    label = "FULL VERSION: custom WAD active (" + (wadBytes.length / 1048576).toFixed(1) + " MB)";
    document.getElementById("wadreset").hidden = false;
    document.getElementById("wadpick").hidden = true;
  } else {
    wadBytes = b64ToBytes("wad-data");
    label = "Shareware Episode 1: Knee-Deep in the Dead";
  }
  document.getElementById("wadlabel").textContent = label;

  try {
    Module.wasmBinary = b64ToBytes("wasm-data");
  } catch (e) {
    fatal("Could not decode the WASM payload: " + e);
    return;
  }
  Module.preRun = [function () {
    var FS = Module.FS || window.FS;
    FS.createDataFile("/", "doom1.wad", wadBytes, true, false);
  }];

  // Execute the engine script (Emscripten glue) synchronously.
  var s = document.createElement("script");
  s.textContent = document.getElementById("engine-code").textContent;
  document.body.appendChild(s);
}

idbGetWad().then(boot, function () { boot(null); });
</script>
</body>
</html>
"""

html = html.replace("@WAD_B64@", wrap(wad_b64))
html = html.replace("@WASM_B64@", wrap(wasm_b64))
html = html.replace("@DOOM_JS@", doom_js)

out_path = OUT / "index.html"
out_path.write_text(html)
print(f"OK {out_path} {out_path.stat().st_size} bytes")
