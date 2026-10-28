# GUT FEELING! — PLEASE DON'T FEED ME!

A personal creative coding project about living with gluten and dairy intolerance, disguised as a Windows 95/98-style operating system.

> **My body is the computer. Food is the input. My digestive system is the operating system.**

Visitors boot into a retro desktop (blue sky, clouds, a grassy hill), meet my digestive system's personal assistant, and feed a digital version of me. Some foods install fine. Others cause error windows, glitches, a draining battery, symptom processes running in the taskbar and, if you keep going, a blue screen of death.

---

## How it works

- **Boot screen:** a BIOS check ("Patience module ... NOT FOUND"), then the *GUT FEELING!* logo. Click or press any key to start.
- **WELCOME TO MY SYSTEM:** "Everything seems normal. Until you feed me." The assistant introduces itself, and **LET'S FEED HER** opens the main app.
- **FEED ME.EXE:** a Paint-style app. My photo is the selected layer on the canvas.
  - **Desktop:** drag a food from the tray onto me or the cloche (a `MOUTH.SYS` target appears while you drag).
  - **Mobile:** tap a food. It's served on the plate and a *"Confirm food selection?"* dialog appears.
  - **The cloche:** the lid is cut out of the photo itself. Hover and it lifts a little; click and it lifts all the way to reveal a random mystery dish.
  - Every food then installs like software: `PROCESSING FOOD...`, `CHECKING COMPATIBILITY...`, a gluten scan, a dairy scan.
- **Reactions:**
  - **Incompatible:** the screen glitches, the window shakes, the photo turns queasy-green, doodles appear around me (lightning, spirals, stink lines, a bloat balloon) and error windows cascade in ("ERROR 404: DIGESTION FAILED.", "Dairy detected. Please reconsider your decisions.").
    - The battery drains and gets stuck at 2%. One more mistake and the system crashes.
    - Symptoms start running as taskbar processes (`Bloating.exe`, `Brain_Fog.exe`, ...). They leak into the OS: Brain Fog blurs the desktop, Fatigue desaturates it and slows the windows down, Stomach Pain makes it twitch. They can't be ended. They close themselves… eventually.
  - **Compatible:** ACCESS GRANTED, hearts, a halo, confetti and +energy.
  - **Check ingredients** (chocolate, sushi, fries): INSUFFICIENT INFORMATION. You get a label checklist to tick before feeding, or you can *Just guess* (and probably lose).
- **SIDE EFFECTS folder:** BLOATING.EXE, FATIGUE.EXE, BRAIN FOG.EXE and STOMACH PAIN.EXE. Hover to run one; it reverses when you leave. On touch screens, tap to toggle.
- **FOODS I MISS:** forbidden files and saved memories (`mac_n_cheese.zip — password protected. Password: no.`). `fresh_bread.wav` plays a crunch.
- **ABOUT MY SYSTEM.TXT:** a personal note in Notepad.
- **Recycle Bin:** drag rejected foods onto it (or onto the reject slot in FEED ME, or press *bin it* in the dialog). You can restore or empty it. Emptied food restocks itself later, like temptation.
- **System Settings:** toggle sound, animations and visual effects, and set the assistant's sarcasm level (the "nice" setting doesn't exist).
- **Extras:**
  - `tummy.wav` growls.
  - The Start menu has *Shut Down Appetite...*.
  - The Paint palette changes the canvas mood.
  - When the desktop sits idle, the assistant peeks out from behind windows and a few notifications show up.

### Food database

| Food | Result |
|---|---|
| Pizza, croissant, cookie | gluten + dairy |
| Pasta, bread | gluten |
| Ice cream, cheese | dairy |
| Strawberries, avocado, rice (plain), banana | compatible |
| Chocolate, sushi, fries | check the ingredients (it depends on how they're made) |

The data lives in the `FOODS` array in `index.html`. Edit it to add foods or change reactions.

---

## Practice concept map

`concept-map/index.html` is a separate page: one map of the 26 concepts behind the practice (the common list in *italic*, my list in **bold**, *__Identity__*, on both, at the centre). Time runs left to right from Heritage to Contemporary perspective, scale runs from Personal up to Socio-political approach, and three rings go from lens to method to form. On GitHub Pages it's at `/concept-map/`.

`practice-onion/index.html` is the newer version: the same concepts drawn as a red-onion slice. Time is the heart, each ring is one step further from it, three branches (Process, Heritage, Contemporary perspective) grow outward, and Identity is the skin where all three arrive. *Tell the story* builds the map one link at a time for presenting. On GitHub Pages it's at `/practice-onion/`.

`practice-tree/index.html` is the tree version, in a folk-print style. Time is the ground, three coloured limbs (Process, Heritage, Contemporary perspective) carry the concepts upward as discs, all three grow into Identity at the crown, and Visual narratives is the star above it. On GitHub Pages it's at `/practice-tree/`.

`practice-nile/index.html` draws the same structure as a river map in the style of a Nile line drawing: three rivers rise from the lake of Time, meet at Identity, and open into the sea as the Visual narratives delta. On GitHub Pages it's at `/practice-nile/`.

`practice-canopy/index.html` is the tree seen from below, in purple and green: Time is the dashed purple trunk, the concepts are leaf clusters along three limbs, they all meet at Identity, and Visual narratives is the open sky above. On GitHub Pages it's at `/practice-canopy/`.

---

## Files

```
index.html          the whole site: HTML, CSS and vanilla JS, with the images embedded as base64
assets/
  rama.jpg          my photo (converted from HEIC, 900×1200)
  assistant.png     the assistant illustration, white background removed
  cloche-lid.png    the cloche lid, cut from the photo so it can lift
README.md
```

`index.html` has no dependencies other than Google Fonts (Silkscreen, Pixelify Sans, VT323, Instrument Serif). If the fonts don't load, it falls back to system fonts. All sounds are synthesized with the Web Audio API, so there are no audio files. There's no backend, build step or API key.

The images are embedded in the last `<script>` tag of `index.html` (`window.EMBEDDED_IMAGES`). If you remove that tag, the page loads the same images from `assets/` instead.

**About the photo:** the background was not removed. The original photo, pink grid wall included, is kept as one layer inside the app window, and the interaction is built on top of it. The page doesn't fake a cutout.

---

## Publish on GitHub Pages

1. Push this repository to GitHub (`index.html` must be at the root).
2. Open **Settings → Pages** on GitHub.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Pick your branch (for example `main`) and the `/ (root)` folder, then **Save**.
5. After a minute the site is live at `https://<username>.github.io/<repository>/`.

To preview locally, open `index.html` in a browser, or run `npx http-server .` and visit the printed address.

---

## Accessibility and comfort

- If your system has *reduced motion* turned on, animations and visual effects start disabled.
- Everything can be switched in **System Settings**.
- Settings and food results are remembered in your browser (localStorage). The site still works when storage is blocked.
- Esc closes the top dialog. Windows, icons and foods are real buttons, so they work with the keyboard.
