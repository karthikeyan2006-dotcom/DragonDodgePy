# Dragon Dodge

**A first-person dodge-and-boss-fight game you play with your body.** No controller, no keyboard — stand in front of a webcam, lean to dodge incoming fireballs, physically jump over ground shots, squat under head-height ones, and punch a dragon out of the sky.

Built in Python on **Panda3D**, with body tracking from **MediaPipe Pose** and **OpenCV**, tuned to run on a **Raspberry Pi 4**.

```
python main.py            # play with your body
python main.py --no-camera  # play with the keyboard
```

![Python](https://img.shields.io/badge/Python-3.9%20%E2%80%93%203.12-blue?logo=python&logoColor=white)
![Panda3D](https://img.shields.io/badge/Panda3D-1.10%2B-orange)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-00A67E)
![Platform](https://img.shields.io/badge/Runs%20on-Raspberry%20Pi%204-c51a4a?logo=raspberrypi&logoColor=white)
![Input](https://img.shields.io/badge/Input-webcam%20%7C%20keyboard-lightgrey)

---

## Contents

- [What it is](#what-it-is)
- [Features](#features)
- [Requirements](#requirements)
- [Install](#install)
- [Run](#run)
- [Controls](#controls)
- [How a round plays](#how-a-round-plays)
- [Difficulty](#difficulty)
- [How the motion control works](#how-the-motion-control-works)
- [Project layout](#project-layout)
- [Assets](#assets)
- [Performance tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## What it is

Dragon Dodge is a two-act game:

1. **Survival** — for 60 seconds, spheres rain down on you. Ground shots you jump over; head-height shots you duck under; anything you get out of the way of scores points.
2. **Boss fight** — the dragon lands. It hovers, breathes fireballs at your feet, and dodges your punches. Land hits to build a combo streak, and the streak makes it far less likely to slip your next punch.

Everything is driven by a single webcam. Your hip position moves the player left and right, a real jump makes the player jump, a squat ducks, and a punch throws a hit. If there's no camera (or no MediaPipe), the game silently falls back to the keyboard and never hard-fails.

## Features

- **Body-controlled, no wearables.** MediaPipe Pose tracks your hips, knees and wrists from a 320×240 camera feed.
- **Real jump physics.** Gravity integration with a snappier fall, a touch of hang-time at the apex, a short input buffer so an early jump still fires on landing, and squash-and-stretch on takeoff and landing.
- **Auto-calibration.** Your standing position becomes the centre of the play field; press **C** to re-centre if you drift.
- **Combo combat.** The dragon starts with a 55% dodge chance. Every hit in a streak knocks 28% off that (floor 5%) and raises your damage, so fast follow-ups are the way to win.
- **Difficulty presets.** Easy / Medium / Hard from the main menu, scaling projectile speed, spawn rate, flame speed and dragon health.
- **Procedural audio.** All 16 sound effects are synthesized with NumPy on first run and cached to disk — no binary audio in git.
- **Pi-friendly rendering.** No multisampling, no vsync stall, no texture padding, a decimated dragon mesh, and a `--quality low` mode that drops shadows, fog and half the particles.
- **A camera thread that can't stall the game.** Pose processing runs off the render loop and only every other frame.

## Requirements

| | |
|---|---|
| Python | 3.9 – 3.12 (MediaPipe wheels are the limiting factor — 3.11 is the safest bet) |
| OS | Linux, macOS, Windows, Raspberry Pi OS 64-bit |
| GPU | Anything Panda3D can open a window on; tested against a Pi 4 |
| Camera | Any UVC webcam for motion control (optional — keyboard works without one) |

Dependencies (see `requirements.txt`): `panda3d`, `panda3d-gltf`, `opencv-python`, `mediapipe`, `numpy`.

## Install

```bash
git clone https://github.com/karthikeyan2006-dotcom/DragonDodgePy.git
cd DragonDodgePy

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Three install notes worth knowing up front:

- **`panda3d-gltf`** is what loads `assets/models/dragon.glb`. If it won't build on your platform, the game still runs — the dragon just falls back to a simple placeholder shape.
- **`assets/models/sun.glb`** (3.8 MB, the sky prop) is optional and lives on the [Releases](https://github.com/karthikeyan2006-dotcom/DragonDodgePy/releases/latest) page instead of the repo — see [Assets](#assets). Skip it and the game draws its placeholder sun.
- **`mediapipe`** ships wheels for most 64-bit platforms, including 64-bit Raspberry Pi OS on a Pi 4. If `pip install mediapipe` fails, you're usually on a Python version with no wheel yet (use 3.11) or a 32-bit OS. The game still runs with `--no-camera` meanwhile.

## Run

```bash
python main.py
```

On a Raspberry Pi 4:

```bash
python main.py --width 960 --height 540
```

| Flag | Effect |
|---|---|
| `--width N`, `--height N` | Window size. Default 1280×720; try 960×540 or 800×450 on a Pi. |
| `--no-camera` | Keyboard only — no webcam or MediaPipe needed. |
| `--debug-cam` | Opens a camera window with the pose skeleton drawn on it, for tuning. |
| `--cam-index N` | Pick a different camera device. Default `0`. |
| `--quality low` | No shadows or fog, half the particles. Closest to the Pi-friendly settings. |

The game opens on a **menu** (Easy / Medium / Hard / Quit). **ESC** during play pauses, with **Resume / Restart / Quit**.

## Controls

| Action | Body (webcam) | Keyboard |
|---|---|---|
| Move left / right | Lean or step left/right of your calibrated centre | <kbd>←</kbd> <kbd>→</kbd> |
| Jump | Physically jump (a sharp rise in your hips) | <kbd>Space</kbd> |
| Duck under head-height shots | Squat — drop your hips or bend your knees | <kbd>↓</kbd> or <kbd>S</kbd> |
| Attack | Punch forward | <kbd>E</kbd> |
| Re-calibrate centre | Stand still, press <kbd>C</kbd> | <kbd>C</kbd> |
| Pause / resume | <kbd>ESC</kbd> | <kbd>ESC</kbd> |
| Restart after game over | <kbd>R</kbd> | <kbd>R</kbd> |

Attacks are edge-triggered: holding the key (or holding your arm out) fires exactly once, so a held input can't spam hits mid-jump. Attacks work while airborne — a jump-punch is a real move, not an animation.

## How a round plays

**Act 1 — Survival (60 s).** Spheres fall in two flavours. Low shots clear if you jump; head-height shots clear only if you duck. Every projectile you cleanly avoid scores **10 points** — dodging is the entire scoring system, so staying mobile is the strategy.

**Act 2 — Boss.** The dragon lands and cycles through idle, attack and dodge states. It hovers around, breathes fireballs that speed up on higher difficulties, and slips punches. Its health bar appears on screen; at 70% and 35% health it gets more aggressive. Break its health to zero and you get the victory screen with your final score.

Getting hit ends the run. **R** restarts.

## Difficulty

Chosen from the menu; Medium reproduces the original tuning, Easy and Hard scale evenly around it.

| | Projectile speed | Spawn rate | Flame speed | Dragon health | Dragon dodge |
|---|---|---|---|---|---|
| **Easy** | ×0.75 | ×1.25 (more gaps) | ×0.80 | ×0.80 | +10% |
| **Medium** | ×1.00 | ×1.00 | ×1.00 | ×1.00 | — |
| **Hard** | ×1.35 | ×0.80 (denser) | ×1.20 | ×1.25 | −10% |

## How the motion control works

`game/pose_tracker.py` runs OpenCV + MediaPipe Pose on its own daemon thread, so a slow frame never stalls the render loop. It processes every other camera frame at 320×240 with the `lite` model (`model_complexity=0`).

- **Lateral dodge** — your hip X relative to a calibrated baseline, scaled, dead-zoned and mapped directly to the player's on-screen X. Step right, you move right.
- **Jump** — a sudden rise in hip Y past a threshold fires one jump pulse; it re-arms only once you're back down, so one hop is one jump rather than a burst.
- **Duck** — a sustained drop in hip height, or bent knees past an angle threshold, holds the crouch state while you stay down.
- **Punch** — a wrist-velocity pulse forward, edge-triggered exactly like the <kbd>E</kbd> key.

Calibration is automatic: whatever pose you hold when a round starts becomes your neutral. If you've drifted across the room, press **C**.

No camera, no MediaPipe, or a failed model download all fall back to keyboard control silently — the HUD tells you which mode you're in.

## Project layout

```
DragonDodgePy/
├── main.py                 CLI entry point (argparse → DragonDodgeApp)
├── requirements.txt
├── assets/
│   ├── models/
│   │   ├── dragon.glb      decimated boss model, feet at the origin
│   │   └── (sun.glb)       sky prop — download from Releases, see Assets
│   └── sfx/                .wav files, synthesized on first run and cached
└── game/
    ├── app.py              game states, arena, menu/HUD, spawning, main loop
    ├── player.py           gravity/jump physics, lateral control, ducking
    ├── projectile.py       survival spheres & dragon flames, hit resolution
    ├── dragon.py           boss AI state machine, model loading
    ├── pose_tracker.py     webcam + MediaPipe thread, calibration, gestures
    ├── particles.py        hit/ember/explosion particle bursts
    ├── audio.py            NumPy sound synthesis + WAV cache
    └── geometry.py         procedural box/cone/sphere/terrain mesh helpers
```

## Assets

- `assets/models/dragon.glb` is a cleaned-up, decimated (~12k triangle) version of the original sculpt, re-centred so its feet sit at the model origin.
- `assets/models/sun.glb` is the sky prop. It's 3.8 MB, so it ships as a [release asset](https://github.com/karthikeyan2006-dotcom/DragonDodgePy/releases/latest) rather than sitting in the repo tree:

  ```bash
  curl -L -o assets/models/sun.glb \
    https://github.com/karthikeyan2006-dotcom/DragonDodgePy/releases/download/v1.0.0/sun.glb
  ```

  Optional. Without it the game logs a note and draws a procedural placeholder sun sphere — same gameplay, slightly plainer sky.
- `assets/sfx/*.wav` are generated by `game/audio.py` on first run. Delete the folder and they'll be rebuilt — nothing in it is hand-made.

**Using your own dragon:** drop a rigged or unrigged `.glb` at `assets/models/dragon.glb`. If it faces the wrong way in the boss fight, change `Dragon.MODEL_YAW_OFFSET` in `game/dragon.py` (try 0 / 90 / 180 / 270) — facing is the one thing that has to be nudged by eye.

## Performance tuning

Already applied in `game/app.py` for a Pi 4:

- Multisampling and anti-aliasing off, no vsync stall, no power-of-two texture padding.
- Boss decimated to ~12k triangles from the original multi-million-vertex sculpt.
- Everything else — floor, rocks, projectiles — is a handful of procedural boxes: no textures, no custom shaders.
- MediaPipe at 320×240 with the lite model, every other frame.

If it still chugs on your hardware, in order of impact:

1. Drop the resolution: `--width 800 --height 450`.
2. `--quality low` — kills shadows and fog, halves particles.
3. In `game/pose_tracker.py`, raise `process_every` to 3 or 4, or lower `cam_width` / `cam_height`.
4. In `game/app.py`, reduce the decorative rock count in `_build_arena`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "No camera" warning, keyboard only | Camera in use by another app, or wrong device. Try `--cam-index 1`. Confirm the feed with `--debug-cam`. |
| Dragon appears as a plain shape | `panda3d-gltf` isn't installed or failed to build. `pip install panda3d-gltf`. |
| `pip install mediapipe` fails | Python version or 32-bit OS. Use Python 3.11 and 64-bit Raspberry Pi OS. |
| Movement drifts or feels off-centre | Stand where you want the middle to be and press <kbd>C</kbd>. |
| Jumps trigger when you don't jump | You're bobbing. Keep the camera steady and level; lower `cam_height` or raise the jump threshold in `pose_tracker.py`. |
| Dragon faces away from you | Set `Dragon.MODEL_YAW_OFFSET` in `game/dragon.py` to 0/90/180/270. |
| Window won't open on a headless Pi | You need a display (X or Wayland). Over SSH, run from the Pi's desktop session. |

## License

No license file is included yet, which means all rights are reserved by default. If you'd like others to reuse this, add one — MIT is a common choice for projects like this — and replace this section with the license name.
