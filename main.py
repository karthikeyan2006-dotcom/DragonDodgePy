"""DragonDodge (Python/Panda3D port with webcam body-motion controls).

    python main.py                    # default 1280x720, webcam control
    python main.py --no-camera        # keyboard-only (arrows/space/E)
    python main.py --debug-cam        # shows a webcam window with pose overlay
    python main.py --width 960 --height 540   # lower res for a weaker Pi
    python main.py --quality low              # no shadows/fog, fewer particles

Controls:
    Move your hips left/right of your calibrated center to dodge - moving
      right moves your character right, moving left moves it left.
    Physically jump to make the player jump.
    E = attack (works mid-jump, i.e. during a real or keyboard jump)
    C = re-calibrate your center position
    ESC = pause / resume
    R = restart after game over / victory
    Arrows/Space also work as a keyboard fallback at any time.
    Start from the main menu; pause any time with ESC for Resume/Restart/Quit.
"""

import argparse
from game.app import DragonDodgeApp


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--width", type=int, default=1280,
                         help="window width (default 1280; try 960 or lower on a Pi 4)")
    parser.add_argument("--height", type=int, default=720,
                         help="window height (default 720)")
    parser.add_argument("--no-camera", action="store_true",
                         help="disable webcam control, use keyboard only")
    parser.add_argument("--debug-cam", action="store_true",
                         help="show a webcam window with the pose skeleton overlay")
    parser.add_argument("--cam-index", type=int, default=0,
                         help="webcam device index (default 0)")
    parser.add_argument("--quality", choices=["high", "low"], default="high",
                         help="'low' turns off shadows/fog and halves particle "
                              "counts - use this on a Raspberry Pi 4 or similar")
    args = parser.parse_args()

    app = DragonDodgeApp(args)
    app.run()


if __name__ == "__main__":
    main()
