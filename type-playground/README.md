# TYPE PLAYGROUND

An experimental typography playground where you shape letters by describing what you want, not by moving sliders.

> "Make the typography look like it's melting." → the letters drip.
> "Now make them overlap." → the dripping letters pile into each other.
> "Less chaotic." → the model softens what it did before.

## Concept

Design tools give you a fixed set of effects. TYPE PLAYGROUND gives you a text prompt. Each instruction goes to a language model (Claude), which **writes new transformation code** for the type: point-by-point outline deformation, per-letter transforms, repetition, SVG filters and paint. The page then runs that code on the vector outlines of your text.

There are no presets and no keyword matching. Ask for "carved from rough stone", "a cheap photocopy", "letters trying to escape the line" or "typed by a nervous robot", and the model works out a visual version from the parts the engine offers. Without a connected model the page shows your type but does not interpret instructions. It never fakes the AI part.

## Features

- **Large central canvas.** It shows "TYPE SOMETHING" by default.
- **Editable text.** Click the canvas or the `TEXT →` field and type. ` / ` starts a new line. Your layers stay applied while you edit the text, because they are code and don't depend on specific letters.
- **Draw your own font.** Switch to **Draw** and write letters on the pad with a trackpad, mouse or finger, using the cap, x-height and baseline guides. Press **Complete the font with Claude** and Claude studies your strokes (slant, proportions, wobble, how curves are built) and draws the rest of the alphabet in the same hand, with lowercase and digits if you ask. Claude's letters are marked "AI" and you can redraw any of them. **Use my handwriting** sets your text in it, and every transformation works on it too. Your letters are saved in this browser.
- **Drag to stretch.** Grab any letter on the canvas and pull it: the far side stays put and the letter stretches toward your pointer like taffy. Each stretch is a layer, so it can be undone, removed or transformed further by later instructions.
- **Built-in effects (no AI needed).** The **Effects** row under the prompt (Sharp edges, Melting, Stretch wide, Balloons, Wavy, Overlap, Chaos, Rough stone, Breathe, Photocopy) applies hand-made transformations instantly, even with no API key. They stack with each other and with everything else, and appear in the layer stack like any other layer. They are fixed presets; anything you describe in your own words goes to the AI.
- **Natural-language prompt.** The field at the bottom asks "What do you want to do with your type?" Press **Apply** or Enter to run it.
- **Air: letters from floating dots.** In the **Air** tab a grid of dots drifts in the air. Press on a dot and drag through others to connect them with lines. Pause, and the shape you made becomes a letter exactly as you drew it: the lines thicken into a solid letterform and it joins **your word**. Nothing is guessed. Press a key (A–Z, 0–9) right after to make that shape your letter in the handwriting font; otherwise it stays a free shape of its own. **Use word** sets the word on the canvas in your shapes.
  - **With a camera**, press **Use camera**: your webcam appears faintly in black and white behind the dots, and you connect them in the air by **pinching** your thumb and index finger (pinch over a button to press it). Hand tracking uses Google's MediaPipe Hand Landmarker, loaded from jsDelivr and Google Cloud Storage only when the camera starts, and runs on your device. Inside a Claude artifact the camera is always blocked, so use the mouse or trackpad there, or open the standalone site.
- **Voice.** Press **Voice** and speak: each sentence you say ("make the font look like jello") is applied as an instruction, and sentences said while Claude is working wait their turn. "Undo", "redo", "reset", "export" and "stop listening" work as spoken commands. In browsers with built-in speech recognition (Chrome, Edge, Safari) the page listens itself; the browser sends the audio to its own speech service to transcribe it. Where the microphone is blocked, such as inside a Claude artifact, the button switches to **hands-free** mode: use your computer's dictation (fn twice on a Mac, Windows + H on Windows) and each sentence is applied when you pause.
- **Cumulative layers.** Each instruction adds a layer on top of the previous ones. The model sees the whole stack, so "more", "less", "undo the wobble" or "same but sharper" work. It can also remove or replace earlier layers.
- **Layer stack.** Click a chip to see the exact code the model wrote, or press × to remove that layer.
- **Undo, redo and reset.** Use the buttons or ⌘/Ctrl+Z and ⇧⌘/Ctrl+Z. Reset can be undone too.
- **Light and dark.** Plain type is black on white, or white on black when the browser or Claude is in dark mode.
- **PNG export.** Saves a high-resolution render (about 3200 px on the long side) of the current composition, including the current frame of an animation.
- **Smooth transitions.** If a change keeps the same outline structure, the shapes morph into their new form. Otherwise they fade in.
- **Motion.** Ask for breathing, floating or wobbling type and the model writes time-based code.
- **Self-repair.** Every response is test-run before it reaches the canvas. If the code throws, returns NaN or produces broken SVG, the error goes back to the model, which can fix it up to twice.

## How it works

```
text ──► canvas raster per glyph ──► traced vector contours (marching edges + simplification)
     ──► layer 1 ─► layer 2 ─► … (code written by the model)
     ──► SVG paths + <use> copies + nested <filter>s ──► screen / PNG
```

Each layer the model returns is JSON with these fields:

| field | what it does |
|---|---|
| `resample` | re-samples the outlines (large spacing gives faceted, angular shapes) |
| `smooth` | neighbour averaging (rounded, soft, blobby shapes) |
| `points` | JS function body run on every outline point, with its outward normal, corner angle, glyph info and time available |
| `glyph` | JS function body run once per letter: move, rotate, scale, skew, per-letter fill and blend |
| `copies` | repeats the whole composition (echoes, shadows, extrusion, misregistration) |
| `style` | fill, stroke, joins, opacity, background and blend mode |
| `defs` | SVG gradients and patterns |
| `filter` | SVG filter primitives (turbulence, displacement, morphology, lighting, gooey thresholds…) |
| `animate` | runs the layer every frame with `t` in seconds |
| `font` | switches between grotesk, serif, mono and condensed faces |

Click any layer chip in the app to read the code behind it.

## Technologies

- One `index.html` file with vanilla JavaScript, HTML and CSS. No framework, no build step, no runtime dependencies.
- **Canvas 2D** draws each glyph so its outline can be traced into polygons. Any font works, and no font-parsing library is needed.
- **SVG** renders the result: paths, `<use>` for copies, nested filters, gradients.
- **Claude Messages API** with structured JSON output, so responses always match the layer schema.
- Google Fonts (Inter Tight, DM Serif Display, Space Mono, Anton). If they can't load, the page uses system fonts.

## Run it

It's a static page, so nothing needs to be installed.

```bash
# any static server works
cd type-playground
python3 -m http.server 8000
# then open http://localhost:8000
```

Opening `index.html` directly from disk (`file://`) also works.

## Connecting the AI

**Inside Claude (no key needed).** When the page is published as a Claude artifact, it uses the viewer's own Claude account through the artifact's built-in Claude access. Claude asks for permission before the first instruction runs, and the **AI** panel only offers a quality setting (Balanced or Best). The steps below are for running the page anywhere else.

Outside Claude, the page calls the Anthropic Messages API (`POST https://api.anthropic.com/v1/messages`). You can connect it in two ways.

### Option A: your own key in the browser (quickest, personal use)

1. Get an API key at <https://platform.claude.com> (Settings → API keys).
2. Open the page and click **AI** in the top-right corner.
3. Paste the key, choose a model and an effort level, and click **Save**.

The key is saved in your browser's `localStorage` and sent only to the endpoint you set. Direct browser calls use the `anthropic-dangerous-direct-browser-access: true` header. Only do this on your own machine. **Never publish a page with a key built into it.**

| setting | default | notes |
|---|---|---|
| Model | `claude-opus-5-5` | best effects; `claude-sonnet-5-5` is faster, `claude-haiku-5-5` is cheapest |
| Effort | `medium` | `low` is snappier, `high` is more inventive but slower |
| Endpoint | `https://api.anthropic.com/v1/messages` | change it to use a proxy (Option B) |

### Option B: a small proxy (for anything you host publicly)

Keep the key on a server and point the page's **Endpoint** setting at the proxy. Leave the key field empty. Here is a dependency-free Node example (Node 18+):

```js
// proxy.mjs  —  ANTHROPIC_API_KEY=sk-ant-... node proxy.mjs
import http from "node:http";

const ALLOW_ORIGIN = process.env.ALLOW_ORIGIN || "*"; // set to your site's origin in production

http.createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", ALLOW_ORIGIN);
  res.setHeader("Access-Control-Allow-Headers", "content-type, anthropic-version, anthropic-beta");
  if (req.method === "OPTIONS") return res.end();
  if (req.method !== "POST") { res.statusCode = 405; return res.end(); }

  let body = "";
  for await (const chunk of req) body += chunk;

  const upstream = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY,
      "anthropic-version": req.headers["anthropic-version"] || "2023-06-01",
      ...(req.headers["anthropic-beta"] ? { "anthropic-beta": req.headers["anthropic-beta"] } : {}),
    },
    body,
  });
  res.statusCode = upstream.status;
  res.setHeader("content-type", "application/json");
  res.end(await upstream.text());
}).listen(8787, () => console.log("proxy on http://localhost:8787"));
```

Then set **Endpoint** to `http://localhost:8787` (or your deployed URL). In production you should also add rate limiting and pin the model on the server.

### What gets sent

Each Apply sends one request containing:

- a system prompt that describes the engine (coordinate system, layer fields, helper functions, rules for the code),
- the current text and the full current layer stack as JSON,
- your instruction.

The request asks for JSON matching the layer schema (`output_config.format`) and sets `fallbacks: "default"`, so a declined request is retried server-side on a fallback model. If an endpoint or model rejects either option, the page drops it and tries again. No chat history is kept between instructions. The canvas state is the memory.

## A note on safety

The page runs JavaScript written by the model with `new Function`, in strict mode, with `window`, `document`, `fetch`, storage and similar globals hidden. This is a guard against accidents, **not a security sandbox**. Model-written SVG is cleaned (no scripts, event handlers, external URLs or `<image>`). Treat the page as a personal creative tool, and use the proxy setup above if other people will use your deployment.

## Files

```
type-playground/
├── index.html   the whole app
└── README.md    this file
```

## Tinkering without the AI

Open the browser console and add a hand-written layer:

```js
TypePlayground.addLayer({
  name: "Wave",
  points: "return [x, y + sin(x * 0.015 + t * 2) * 25];",
  animate: true,
});
```
