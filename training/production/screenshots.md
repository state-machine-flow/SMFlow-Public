# Screenshots

Every lab ships its images in `<lab>/images/`, referenced from the lab's markdown. Shots that
haven't been captured yet are **placeholder PNGs** that render the shot's ID and its spec, so the
lab reads coherently before a single screenshot exists and nobody has to guess what a slot was for.

**Backfilling is one step: overwrite the PNG.** No markdown edit, no path change, no manifest
update.

---

## The manifest

[`shots.json`](shots.json) is the source of truth. One entry per shot:

```json
{
  "id":    "1.06",
  "file":  "wiring.png",
  "title": "Drawing a wire",
  "spec":  "Mid-drag from StartButton.value toward NOT.in, with whatever the editor shows for a valid target port (highlight / snap). Catch it in motion.",
  "frame": "Two nodes, tight",
  "alt":   "Dragging a connection from the StartButton value port to the NOT input port"
}
```

| Field | Purpose |
|---|---|
| `id` | `<lab>.<n>`, stable forever. Appears on the placeholder and in an HTML comment in the lab |
| `file` | Filename inside `<lab>/images/` |
| `title` | Short label, shown on the placeholder |
| `spec` | What to capture. Written for whoever holds the camera, which may be you in six weeks |
| `frame` | Crop and composition |
| `alt` | Alt text. Goes into the published markdown — write it for a screen reader, not as a caption |

## Generating

```
cd training/production
python make-placeholders.py            # fill in anything missing
python make-placeholders.py --status   # progress report, writes nothing
python make-placeholders.py --force    # redraw placeholders after editing specs
python make-placeholders.py --lab lab-01-first-flow
```

Needs Pillow (`pip install pillow`).

**A real screenshot is never overwritten.** Placeholders carry a `smflow-placeholder` key in their
PNG metadata; the script only touches files that have it. Once you drop in a real capture, every
future run skips that slot, including `--force`.

So `--status` is also your capture progress board:

```
lab-00-concepts: 3/14 real screenshots
lab-01-first-flow: 17/17 real screenshots
```

## Adding a shot to a lab

1. Add the entry to `shots.json`.
2. Run `python make-placeholders.py`.
3. Reference it in the lab:

```markdown
<!-- shot 1.06 -->
![Dragging a connection from the StartButton value port to the NOT input port](images/wiring.png)

*Drawing a wire from `StartButton.value` to `NOT.in`.*
```

The HTML comment carries the shot ID so you can find the slot from the manifest and vice versa. The
italic line underneath is the **caption** — what the reader gets — and is deliberately different
from `alt`, which is what a screen reader gets. Don't make them the same sentence.

## Capture conventions

Consistency across 13 labs matters more than any individual shot being perfect.

| | |
|---|---|
| **Resolution** | Capture at 2× the delivered size. 1600×900 is the placeholder size and a good floor |
| **Editor** | Dark theme, default. 150% UI scale so text survives downscaling |
| **Terminal** | Light theme, 18pt minimum — it reads as distinct from the editor at a glance |
| **Code shots** | One file, full frame, 20pt+. Must be legible on a phone |
| **Hardware** | Overhead, plain mat, breadboard power rails left-to-right |
| **Chrome** | Crop out the OS title bar, taskbar, and any personal paths or filenames |
| **Project names** | Projects are named `lab-NN.smflow` so a reader's recent-projects list stays legible. Don't capture a shot where yours is called `test3.smflow` |

### Things that quietly ruin a shot

- **A hung-looking terminal.** For a command whose success is *no output* — the grep in 1.12, the
  diff in 1.14 — include the next prompt in frame. Otherwise it reads as still running.
- **Round numbers in the simulator.** A scan counter sitting at `1000` looks staged. Let it land
  somewhere arbitrary.
- **Stale UI.** If the editor changes, regenerate affected shots rather than letting one lab show
  last year's inspector.
- **Personal data.** Check the window title, the path bar, and any visible file tree.

## Annotations

Callouts, arrows, and numbered markers are welcome where the shot is making an argument — the
editor tour (0.01), node anatomy (0.06), the pipeline (0.14). Keep them in one accent color, use
the same arrow weight throughout the series, and never obscure the thing being pointed at.

Shots marked **DIAGRAM** in their spec are illustrations, not captures. They still live in
`images/` and still work the same way.
