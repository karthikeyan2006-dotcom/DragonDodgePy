# Dragon Dodge

**A first-person dodge-and-boss-fight game you play with your body.** No controller, no keyboard. Stand in front of a webcam, lean to dodge incoming spheres, jump over ground shots, duck under head-height ones, and punch a dragon out of the sky.

Built in Python with **Panda3D**, body tracking from **MediaPipe Pose** and **OpenCV**, and tuned to run on a **Raspberry Pi 4**.

```bash
python main.py                # play with your body
python main.py --no-camera    # play with the keyboard
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

1. **Survival.** For 60 seconds, spheres rain down on you. Ground shots you jump over; head-height shots you duck under. Every sphere you get out of the way of scores points.
2. **Boss fight.** The dragon lands. It hovers, breathes fireballs at your feet, and slips your punches. Land hits in quick succession to build a combo streak. The streak makes it much harder for the dragon to dodge your next punch.

A single webcam drives everything. Your body position moves the player left and right, a real jump makes the player jump, a squat ducks, and a punch throws a hit. If there is no camera, or the body-tracking library isn't installed, the game falls back to the keyboard and never hard-fails.

## Features

- **Body control, no wearables.** MediaPipe Pose tracks your shoulders, hips, knees, ankles and wrists from the webcam feed.
- **Real jump physics.** Gravity with a snappier fall, a touch of hang-time at the top of the jump, a short input buffer so a jump pressed just before landing still fires, and a squash-and-stretch effect on takeoff and landing.
- **Auto-calibration.** Your position when tracking starts becomes the centre of the play field. Press **C** to re-centre if you drift.
- **Combo combat.** The dragon starts with a 55% chance to dodge a punch. Each hit in a streak lowers that chance by 28 points (down to a 5% floor) and raises your damage, so fast follow-ups win fights.
- **Three difficulty presets.** Easy, Medium and Hard change projectile speed, spawn rate, fireball speed and the dragon's health and dodge chance.
- **Procedural audio.** All 16 sound effects are synthesized with NumPy on first run and cached to disk, so the repository contains no binary audio.
- **Pi-friendly rendering.** Multisampling and vsync are off, the dragon mesh is decimated, the scenery is built from simple shapes, and `--quality low` drops shadows, fog and half the particles.
- **A camera that can't stall the game.** Pose processing runs on its own thread, so a slow camera frame never freezes the picture.

## Requirements

| | |
|---|---|
| Python | 3.9 to 3.12. MediaPipe wheels are the limiting factor; 3.11 is the safest choice. |
| OS | Linux, macOS, Windows, or Raspberry Pi OS 64-bit |
| Graphics | Anything Panda3D can open a window on. Tuned for a Raspberry Pi 4. |
| Camera | Any USB or built-in webcam for body control. Optional: the keyboard works without one. |
| Internet | Needed once, the first time body tracking starts, to download the pose model. |

Python packages (see `requirements.txt`): `panda3d`, `panda3d-gltf`, `opencv-python`, `mediapipe`, `numpy`.

## Install

```bash
git clone https://github.com/karthikeyan2006-dotcom/DragonDodgePy.git
cd DragonDodgePy

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Two install notes:

- **`panda3d-gltf`** loads the dragon model (`assets/models/dragon.glb`). If it won't install on your platform, the game still runs, but the dragon appears as a simple placeholder shape.
- **`mediapipe`** ships wheels for most 64-bit platforms, including 64-bit Raspberry Pi OS on a Pi 4. If `pip install mediapipe` fails, you are probably on a Python version without a wheel (try 3.11) or a 32-bit OS. Use `--no-camera` in the meantime.

## Run

```bash
python main.py
```

On a Raspberry Pi 4, use a smaller window:

```bash
python main.py --width 960 --height 540 --quality low
```

| Option | Effect |
|---|---|
| `--width N`, `--height N` | Window size. Default 1280 x 720. Try 960 x 540 or 800 x 450 on a Pi. |
| `--no-camera` | Keyboard only. No webcam or MediaPipe needed. |
| `--debug-cam` | Opens a camera window with the pose skeleton drawn on it, for tuning. |
| `--cam-index N` | Picks a different camera. Default `0`. |
| `--quality low` | No shadows or fog, half the particles. |

The game opens on a **menu** with Easy, Medium, Hard and Quit. Press **ESC** during play to pause, then choose **Resume**, **Restart** or **Quit**.

## Controls

| Action | Body (webcam) | Keyboard |
|---|---|---|
| Move left / right | Lean or step left or right of your calibrated centre | <kbd>←</kbd> <kbd>→</kbd> |
| Jump | Jump for real | <kbd>Space</kbd> |
| Duck under head-height spheres | Squat: drop your hips or bend your knees | <kbd>↓</kbd> or <kbd>S</kbd> |
| Attack | Punch forward, toward the camera | <kbd>E</kbd> |
| Re-centre | Stand where you want the middle to be, then press | <kbd>C</kbd> |
| Pause / resume | <kbd>ESC</kbd> | <kbd>ESC</kbd> |
| Restart after game over or victory | <kbd>R</kbd> | <kbd>R</kbd> |

Attacks fire once per press. Holding the key (or holding your arm out) does not spam hits, so a held input can't multiply during a jump. Attacks work in the air, so a jump-punch is a real move.

## How a round plays

**Act 1: Survival (60 seconds).** Spheres come in two kinds. Ground spheres are cleared by jumping. Head-height spheres are cleared by ducking, and jumping doesn't help. Spheres also steer slightly toward you, so you have to keep moving. Each sphere you clear scores **10 points**. Staying mobile is the whole strategy.

**Act 2: Boss.** The dragon lands and cycles through idle, attack and dodge moves. It hovers from side to side and breathes fireballs that get faster on harder difficulties. Its health bar appears at the top of the screen, and the dragon becomes more aggressive as its health drops. Bring its health to zero to win and see your final score.

Getting hit ends the run. Press **R** to try again.

## Difficulty

Chosen from the menu. Medium is the baseline; Easy and Hard scale evenly around it.

| | Sphere speed | Spawn rate | Fireball speed | Dragon health | Dragon dodge chance |
|---|---|---|---|---|---|
| **Easy** | 75% | 125% (more gaps) | 80% | 80% | +10 points |
| **Medium** | 100% | 100% | 100% | 100% | none |
| **Hard** | 135% | 80% (denser) | 120% | 125% | -10 points |

## How the motion control works

The tracking code in `game/pose_tracker.py` runs OpenCV and MediaPipe Pose on its own thread. It reads the webcam, mirrors the image so it behaves like a mirror, and looks at your body landmarks.

- **Moving sideways.** The game tracks the centre of your shoulders and hips. Its horizontal offset from the calibrated centre sets where your character stands. Step right, and you move right.
- **Jumping.** A quick upward movement of your body fires one jump. The tracker re-arms only after you come back down, so one hop is one jump.
- **Ducking.** A sustained drop in your body height, or clearly bent knees, holds the crouch while you stay down.
- **Punching.** Extending either wrist well away from its shoulder fires one punch. Pulling the arm back re-arms it, the same way a key press does.

Calibration happens automatically when tracking starts. Keep your full body in view and stand where you want the centre to be. If you drift across the room, press **C**. The centre also adjusts slowly while you stand still.

If the camera or body-tracking library is unavailable, or the pose model can't be downloaded, the game falls back to the keyboard without stopping. The on-screen camera status line shows which mode you are in.

## Project layout

```
DragonDodgePy/
├── main.py                 Command-line entry point
├── requirements.txt        Python packages
├── assets/
│   ├── models/
│   │   ├── dragon.glb      Boss model, feet at the origin
│   │   ├── sun.glb         Sky prop, texture reduced to keep the repo small
│   │   └── pose_landmarker_lite.task   Pose model, downloaded on first use
│   └── sfx/                Sound effects, synthesized on first run and cached
└── game/
    ├── app.py              Game states, arena, menus, HUD, spawning, main loop
    ├── player.py           Jump physics, sideways movement, ducking
    ├── projectile.py       Spheres and fireballs, hit resolution
    ├── dragon.py           Boss behaviour and dodge/combo logic, model loading
    ├── pose_tracker.py     Webcam and MediaPipe thread, calibration, gestures
    ├── particles.py        Hit, ember and explosion particle bursts
    ├── audio.py            Sound synthesis and WAV cache
    └── geometry.py         Procedural box, cone, sphere and terrain shapes
```

## Assets

- `assets/models/dragon.glb` is a cleaned-up, decimated (about 12,000 triangles) version of the original sculpt, centred so its feet sit at the model origin.
- `assets/models/sun.glb` is the sky sun. Its texture was reduced from 4096 x 2048 to 1024 x 512, which shrank the file from 3.8 MB to 278 KB. It sits far away, so the reduction isn't visible in play. The full-resolution original is attached to the [v1.0.0 release](https://github.com/karthikeyan2006-dotcom/DragonDodgePy/releases/tag/v1.0.0).
- `assets/sfx/*.wav` are generated on first run. Delete the folder and they will be rebuilt.

**Using your own dragon:** place a `.glb` file at `assets/models/dragon.glb`. If the dragon faces the wrong way, change `Dragon.MODEL_YAW_OFFSET` in `game/dragon.py` and try 0, 90, 180 or 270.

## Performance tuning

The game already uses these settings for a Raspberry Pi 4:

- Multisampling and vsync are off, and textures are not padded to powers of two.
- The boss is decimated to about 12,000 triangles.
- Everything else (floor, rocks, spheres, scenery) is built from simple shapes with no textures or custom shaders.
- Body tracking uses the lightweight MediaPipe model and runs on a separate thread.

If the game still runs slowly, try these in order of impact:

1. Lower the window size: `--width 800 --height 450`.
2. Use `--quality low` to remove shadows and fog and halve the particles.
3. In `game/app.py`, pass `process_every=2` (or 3) when creating the `PoseTracker`, so pose detection runs on fewer camera frames. Lowering `cam_width` and `cam_height` in `game/pose_tracker.py` also helps.
4. In `game/app.py`, reduce the number of decorative rocks in `_build_arena`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "No camera" message, keyboard only | Another app may be using the camera, or the wrong device is selected. Try `--cam-index 1`, and check the feed with `--debug-cam`. |
| Camera status says "no person detected" | Step back so your head to knees are visible, and make sure the lighting is decent. |
| Dragon appears as a plain shape | The `panda3d-gltf` package isn't installed. Run `pip install panda3d-gltf`. |
| `pip install mediapipe` fails | Use Python 3.11 and 64-bit Raspberry Pi OS. |
| Pose model never downloads | The first run needs internet access. Check the connection, then restart. |
| Movement drifts or feels off-centre | Stand where you want the middle to be and press <kbd>C</kbd>. |
| Jumps trigger when you don't jump | You're bobbing. Keep the camera steady, and raise the jump threshold `JUMP_THRESHOLD` in `DEFAULT_CONFIG` (`game/pose_tracker.py`). |
| Dragon faces away from you | Set `Dragon.MODEL_YAW_OFFSET` in `game/dragon.py` to 0, 90, 180 or 270. |
| Window won't open on a headless Pi | A display is required (X or Wayland). Over SSH, run the game from the Pi's desktop session. |

## License

No license file is included yet, so all rights are reserved by default. To allow others to reuse this project, add a license file. MIT is a common choice for projects like this. Then replace this section with the license name.
