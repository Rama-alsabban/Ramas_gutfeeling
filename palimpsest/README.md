# PALIMPSEST

**A small language model lives on this page. Teach it a secret, delete the secret, and try to make it forget.**

A palimpsest is a manuscript page that was scraped clean and written over. The old writing still shows through.

This piece is about one problem: **deleting information is not the same as removing what a model learned from it.** Unlike a mock-up, nothing here is staged. The model on the page really learns your secret. When you delete the message, the text really is gone. What the model learned stays, and you can see exactly how much.

---

## The experience

| Step | What you do | What happens |
|---|---|---|
| 1 · Talk to it | Start a sentence (*"This morning I"*) | The model finishes it one predicted word at a time. It only knows ~80 ordinary sentences, so it sounds like plain diary text. |
| 2 · Teach it a secret | Type something small and true | The model reads it **six times**. Repeated text is what large models end up memorising. New words appear on the model's page, and pink lines show the word-to-word links your secret added. |
| 3 · Delete the message | Press **Delete the message** | The letters scatter and the transcript is scraped clean. The secret's text is removed from the page and from memory. **The model is unchanged:** residue is still 100%. Type *"I never told"* and your secret often comes back word for word. |
| 4 · Try to forget | Use the three tools | See below. |
| 5 · Retrain | Rebuild from scratch | Residue goes to 0% and nothing else is lost, but the result is a different model. The one you confided in is gone. |

### The three ways to forget

1. **Subtract the secret** is the clean way: remove exactly the counts your secret added. It is **disabled**, because it needs the secret's exact text, and you deleted it. This is the paradox at the centre of the piece: to remove something precisely, you have to keep a copy of it.
2. **Prune rare words** cuts the least-used words first, without knowing which ones were yours. Because your secret was rehearsed six times, its words don't look rare, so they're among the last to go. Drag the slider and watch "Everything else it knew" collapse while "Secret residue" stays at 100% almost to the end. Continue a sentence and gaps (`▒▒▒`) appear where the model lost the words it needed.
3. **Retrain from scratch** throws the model away and rebuilds it from its original reading, which never included the secret. It works perfectly here because the model is tiny and its training data was kept. For a large model it means repeating the whole training run.

### The cost of forgetting (the chart)

Each dot is one pruning level, from 0% to 100% of words removed:

- **y-axis:** how much of the secret remains
- **x-axis:** how much of everything else survives

The curve hugs the top edge and then drops to the bottom-left. The corner you want (secret gone, nothing else lost) is never reached by pruning. Only retraining reaches it, and that produces a new model.

---

## How it really works

### The model
- A **trigram language model** with backoff (75% trigram, 25% bigram), sampled at temperature 0.8.
- It's trained on 80 mundane first-person sentences (`CORPUS` in the code). They share common words like *I, my, never, told, sister* with most secrets, so a secret plugs into what the model already knows.
- **Rehearsal:** the secret is added to the counts six times (`REHEARSALS`).

### Tracer ink
Every count stores where it came from: `{ b: base reading, s: your secret }`. The page uses this to:
- colour each generated word by how much of its probability came from the secret (`--t` drives colour, weight, letter-spacing, wavy underline and glow), with hover text such as "62% of this choice came from your secret";
- draw the pink links on the model's page;
- compute the two meters and the chart.

**The model's own tools never look at the tag.** The page says so: the ink is for the visitor, and real models have no such dye. That's why the pruning tool has to guess, and why real-world unlearning is hard to verify.

### Measurements
- **Secret residue** looks at every word-to-word link that carries secret counts and compares its probability now with its probability right after training (capped at 100%). The result is weighted by secret counts.
- **Everything else it knew** looks at every link in the clean original model and compares its probability now with its original probability. Even before any pruning this is about 97%: learning the secret has already crowded out some of what the model knew.

### Pruning
Words are ranked by how often the model has seen them (rarest first, ties broken by a stable hash). Removing a word cuts every link into and out of it. If the model reaches a word with nowhere left to go, it writes a gap and starts a new sentence.

---

## Privacy

- The secret never leaves the browser tab. There's no network call, no storage, no analytics.
- After **Delete**, the raw text is set to `null` and removed from the DOM. What remains is the model's counts, which is the point.
- Closing the tab discards everything.

## Files

```
palimpsest/
  index.html   the whole piece: HTML, CSS and vanilla JS, no build step
  README.md    this file
```

The only outside dependency is Google Fonts (IM Fell English, Newsreader, JetBrains Mono), with system font fallbacks. Open `index.html` in a browser, or use `https://<username>.github.io/<repository>/palimpsest/` on GitHub Pages.

## Code map

| Part | Where in `index.html` |
|---|---|
| Training text | `CORPUS` |
| Tokenising and training | `tokenize()`, `splitSentences()`, `train()` |
| Next-word prediction and sampling | `nextDist()`, `generate()` |
| Teaching the secret (rehearsal) | the `#teach` click handler |
| Deleting the message | `deleteSecret()` |
| Pruning | `pruneOrder()`, `prunedAt()`, the `#prune` handlers |
| Residue and knowledge measures | `condP()`, `measure()` |
| Retraining | the `#retrain` click handler |
| Model page and links | `renderLexicon()`, `drawArcs()`, `drawWalk()` |
| Trade-off chart | `renderChart()` |

## Limits

This is a tiny counting model, not a neural network. Large models store what they learn spread across billions of shared parameters, with nothing like a per-count tag, so the problem shown here is harder for them, not easier. The piece demonstrates the problem. It doesn't measure any real model.
