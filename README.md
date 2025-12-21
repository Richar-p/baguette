# BAGUETTE

The project is to have a tool easier to use than Compose, for typing accent on linux with qwerty keyboard.

## Installation

```bash
pip install -r requirement.txt
```

### Wayland Users - Important Setup Required!

If you're using Wayland, you need to add your user to the `input` group for keyboard capture to work:

```bash
sudo usermod -a -G input $USER
```

Then **log out and log back in** (or reboot) for the change to take effect.

See [SETUP.md](SETUP.md) for detailed setup instructions and troubleshooting.

## Usage

```bash
python3 main.py
```

Type a vowel (a, e, i, o, u) followed by space to open the accent selection window. Press a number (1-5) to select the accent.

Press CTRL+C to quit.

WIP
 
# TODO:

- Replace french logs (sry, baguette)
- Fix `RuntimeError: wrapped C/C++ object of type AccentWindow has been deleted` error
- ~~Add the possibility to quit the tool without kill every process~~ ✓ Done (CTRL+C)
- Case insensivity
- Create settings page
- Add more accents
- Create minimized mode