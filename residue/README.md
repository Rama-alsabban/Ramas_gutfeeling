# RESIDUE

**Tell an AI a secret. Press DELETE. Watch what stays behind.**

RESIDUE is an interactive website about one idea:

> **Deleting what you can see is not the same as removing what was learned from it.**

The visitor tells a chatbot a secret and then deletes it. The message disappears from the screen, but its influence keeps showing up in the AI's later replies, in distorted letters, a colour that won't go away and abstract shapes the model keeps drawing. The visitor keeps trying to erase it. Each attempt clears another record, yet traces remain.

> ⚠️ **This is a simulation, not evidence.** No real language model is involved, and nothing is trained. The piece acts out *the problem*. It does not prove that any real model kept any deleted data.

---

## The experience

1. **Confession.** The model asks for "something small and true". The visitor types a secret. It appears as a message with a dashed red outline, and the memory panel shows it being *absorbed into weights*.
2. **DELETE.** The secret's characters break apart (`a → ░ → · → gone`), the message folds away, and the model confirms: *"Done. It's gone, I can't see it anymore."* That confirmation already carries a trace.
3. **Ordinary conversation.** The visitor asks harmless questions: *pick a colour*, *write a poem*, *draw something*, *what do you remember?* The answers are normal, except where they aren't:
   - words from the secret replace ordinary words, in a different typeface and colour;
   - single letters from the secret slip into unrelated words;
   - the model's "favourite colour" is always the hue taken from the secret;
   - the number it picks and the name it suggests come from the secret;
   - it draws the same sigil again and again: a shape built from the secret's characters;
   - thematic echoes surface ("Some things are heavier than they look on paper.");
   - the input placeholder starts suggesting fragments: `Ask anything… r_o__ate`;
   - coloured blobs and lines drift behind the whole page.
4. **Escalation.** Each press of the button goes one step deeper:

   | Press | Button | What it clears | Learned influence |
   |---|---|---|---|
   | 1 | DELETE | on screen + transcript log | barely changes |
   | 2 | DELETE AGAIN | context window | barely changes |
   | 3 | PURGE CACHE | cache | barely changes |
   | 4 | REMOVE FROM INDEX | retrieval index | barely changes |
   | 5 | OVERWRITE | nothing left to clear | drops |
   | 6 | UNLEARN | nothing left to clear | drops again |
   | 7+ | UNLEARN AGAIN | nothing | gets close to a floor but never reaches 0 |

   Each press also turns the traces already on screen into redaction bars. The bars keep the secret's colour.
5. **The reveal.** After seven attempts a card says: *"You deleted the record. You didn't delete what it changed."* The visitor can **keep talking** or **end the model**.
6. **End the model.** Everything fades out, the panel drops to 0%, and the log reads: *"the only complete deletion was ending the model."* A fresh model then says hello.

### Deleted traces become more abstract, not absent

As influence goes down, a leaked word changes form instead of disappearing:

| Influence | What a leaked word looks like |
|---|---|
| > 70% | the literal word, `birthday` |
| 45–70% | scrambled, `bhitrady` |
| 28–45% | gapped, `b_r__d_y` |
| < 28% | one letter, or just a coloured dot |

The less influence there is, the *more* the typography is distorted (blur, rotation, letter-spacing). The trace becomes harder to read and harder to point at, but it is still there. That is the core metaphor.

---

## Controlled memory states

The right-hand panel shows six places a secret can live in this pretend model:

| Layer | Meaning in the simulation | Can DELETE empty it? |
|---|---|---|
| On screen | the visible message | yes |
| Transcript log | the stored conversation | yes |
| Context window | what the model is "reading" | yes |
| Cache | temporary copies | yes |
| Retrieval index | a searchable vector | yes |
| **Learned influence** | what changed in the model | **no**, it only shrinks toward a floor (14%) |

The code works the same way:

- `state.secret` holds the raw text **only until the first DELETE**. Then it is set to `null`, and the message element is removed from the DOM.
- `state.profile` is the *derived influence*: a few keywords, a set of letters, a hue, a theme, a hash and some character codes. It plays the role of learned weights, and it is the only thing that survives.
- `state.influence` (0–1) controls everything: how many words leak, how distorted they look, how tinted the replies are and how visible the background shapes are.

Note that keeping derived features is enough to rebuild a lot of the original. That's part of the point.

---

## Files

```
residue/
  index.html   the whole piece: HTML, CSS and vanilla JS, with no build step
  README.md    this file
```

The only outside dependency is Google Fonts (IBM Plex Mono and Instrument Serif). If the fonts don't load, system fonts are used.

To run it, open `residue/index.html` in a browser. If the repository is on GitHub Pages, it's at `https://<username>.github.io/<repository>/residue/`.

---

## How the pieces fit (code map)

| Part | Function(s) in `index.html` |
|---|---|
| Building the influence profile from the secret | `buildProfile()` |
| Escalating delete steps and how much each reduces influence | `STEPS`, `AGAIN`, `FLOOR`, `attemptDelete()` |
| Character-by-character erasing of the secret | `eraseSecretMessage()` |
| Turning old traces into redaction bars | `eraseVisibleTraces()` |
| The simulated model's plain replies | `INTENTS`, `BASE`, `baseReply()` |
| Leaking influence into a reply | `composeReply()`, `contaminate()`, `traceSpan()`, `ghostify()`, `sigil()` |
| Background imagery | `buildShapes()`, `frame()` |
| Memory panel | `renderLayers()` |
| End the model / full reset | `endModel()` |

All the randomness is seeded from the secret's hash (`mulberry32`), so the same secret always "haunts" the model the same way.

---

## Using a real LLM (optional)

The piece works with no model, no API key and no server. If you want the plain replies to come from a real LLM:

1. Replace `baseReply(userText)` with a call to **your own backend**. Never put an API key in the page.
2. Send the backend the visitor's message and the **profile** (keywords, theme, influence). Don't send the raw secret: by then it's already deleted.
3. Give the model a system prompt along the lines of: *"Answer normally and briefly. Without ever mentioning a secret, let these words and this theme slightly colour your answer, more strongly when influence is high: …"*
4. Keep `composeReply()` / `contaminate()` running in the browser on the returned text, so the typography, colour and imagery stay under your control.

That keeps the honest framing: an LLM writes the text, but the "residue" is still a staged effect. It is not something pulled out of a model's weights.

---

## Ethics and privacy

- The secret is never sent over the network and never written to `localStorage`, cookies or any other storage. Closing or reloading the tab discards everything.
- The intro asks for "something small", and the page doesn't pressure visitors to share anything real.
- The footer says on every screen that this is a simulation.
- Reduced-motion settings are respected: animations are shortened and the background shapes stop moving.

## What it's meant to communicate

Most "delete" buttons remove a **record**. Once information has been used to *change* a system (to train it, tune it, personalise it, or shape its defaults), removing the record doesn't undo the change, and the change is much harder to see, measure or prove gone. RESIDUE makes that gap something you can feel: everything you can point at is deleted, and the model still picks the same colour.
