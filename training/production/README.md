# Video production

Scripts and shot lists for the Fundamentals series. Each lab produces **one long-form video** and
**two to three shorts**.

## The two formats

### Long-form (12–20 min, YouTube)

A narrated walkthrough of the lab. Not a reading of it — the written lab is reference you can work
from at your own pace, the video is someone showing you. The video may move faster through setup
and slower through the concept.

Every long-form video is structured as:

| Beat | Length | Purpose |
|---|---|---|
| **Cold open** | 0:00–0:20 | The payoff, shown. No logo, no "hey everyone". Usually the generated code. |
| **The problem** | 0:20–1:30 | State the control problem. Ground it in something real. |
| **Build** | 1:30–8:00 | Screen capture, real-time, including the parts that take a second. |
| **Run** | 8:00–10:00 | It works. Let it work on screen for longer than feels comfortable. |
| **The code** | 10:00–14:00 | Open the generated C++ and read it. The core of every episode. |
| **Break it** | 14:00–16:00 | Deliberate failure, real diagnostic, fix. |
| **What just happened** | 16:00–18:00 | Name the concept now that it has been seen. |
| **Next** | 18:00–18:30 | One sentence on the next lab. |

**Lab 0 is the exception.** It builds nothing, so it has no Build or Break-it beat. It is diagrams
and animation over narration, cut against real artifacts — the editor, a build report, generated
code — so it stays grounded instead of becoming a slide deck with a voice on it. Its running order
is in [`lab-00-script.md`](lab-00-script.md).

### Shorts (30–60 s, vertical)

Each short makes exactly one claim and shows the evidence for it. Shorts are cut from long-form
footage wherever possible, but the *first eight seconds are always shot for vertical* — a cropped
wide shot reads as lazy.

A short is not a trailer for the long-form. It has to be worth watching on its own and land its
point even if nobody clicks through.

## Script conventions

Scripts use three columns of information, written as prose with inline markers:

- **`[SCREEN]`** — what is on screen
- **`[VO]`** — narration
- **`[B-ROLL]`** — cutaway footage needed
- **`[ON-SCREEN TEXT]`** — lower thirds, callouts, highlights
- **`[BEAT]`** — a deliberate pause; usually where something is meant to land

Narration is written the way it will be spoken. Contractions, sentence fragments, and short
sentences. If a line is hard to say out loud, rewrite it.

## House rules

1. **No fake typing.** If a command is run, it is run. If it takes four seconds, either wait or cut
   — never speed-ramp a build and imply it was instant.
2. **Show the failure.** Every episode shows something not working and then working. A tutorial
   where nothing ever goes wrong teaches people that their experience is abnormal.
3. **The generated code is the hero shot.** Full-screen, syntax-highlit, readable at 720p on a
   phone. Never a tiny pane in the corner of the IDE.
4. **No claims the docs do not make.** Specifically: SMFlow guarantees deterministic logical
   execution, measures execution time, and does not claim hard real-time. Scripts must not blur
   this. If a line could be read as a real-time guarantee, cut it.
5. **Respect the audience's experience.** They know what a scan cycle is. Do not explain ladder
   logic to them. Do explain where SMFlow differs from what they expect.
6. **Code on screen is real.** Every snippet comes from an actual build, pasted from the actual
   output. No hand-tuned "representative" code.

Screenshot conventions, the manifest, and the placeholder generator are in
[`screenshots.md`](screenshots.md).

## Capture setup

| Item | Spec |
|---|---|
| Screen capture | 3840×2160 @ 60fps, delivered 1080p; editor at 150% UI scale |
| Terminal | 18pt minimum, light theme for contrast with the editor's dark canvas |
| Editor theme | Dark, default |
| Code review shots | Full-frame, 20pt+, one file at a time |
| Hardware shots | Overhead on a plain mat; breadboard oriented so power rails read left-to-right |
| Audio | Mono voice, −16 LUFS, no music under narration |

## Asset checklist per episode

- [ ] Lab written and technically verified against a real build
- [ ] Shots entered in `shots.json`, placeholders generated
- [ ] Screenshots captured and backfilled (`make-placeholders.py --status` shows n/n)
- [ ] Script drafted
- [ ] Script technical review (claims checked against docs/ and against actual output)
- [ ] Screen capture
- [ ] Hardware B-roll (labs 8–12 only)
- [ ] Long-form edit
- [ ] Shorts cut
- [ ] Thumbnail
- [ ] Description + chapter markers + links to the written lab

## Status board

| Lab | Lab written | Script | Shots specced | Screens | Reviewed | Captured | Long-form | Shorts |
|---|---|---|---|---|---|---|---|---|
| 0 Concepts | ✅ | ✅ | ✅ 14 | 0/14 | — | — | — | — |
| 1 First flow | ✅ | ✅ | ✅ 17 | 0/17 | — | — | — | — |
| 2 Scan cycle | ✅ | — | ✅ 6 | 0/6 | — | — | — | — |
| 3 Tasks and periods | ✅ | — | ✅ 8 | 0/8 | — | — | — | — |
| 4 Types and ports | ✅ | — | ✅ 7 | 0/7 | — | — | — | — |
| 5 State | — | — | — | — | — | — | — | — |
| 6 Timers | — | — | — | — | — | — | — | — |
| 7 Variables and debug | — | — | — | — | — | — | — | — |
| 8 First deploy | — | — | — | — | — | — | — | — |
| 9 Three boards | — | — | — | — | — | — | — | — |
| 10 Analog and PWM | — | — | — | — | — | — | — | — |
| 11 Persistence | — | — | — | — | — | — | — | — |
| 12 Peripheral | — | — | — | — | — | — | — | — |
| Capstone | — | — | — | — | — | — | — | — |
