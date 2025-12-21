# Baguette - Setup Instructions

## For Wayland Users

Baguette uses `evdev` for keyboard capture on Wayland systems. This requires your user to be in the `input` group.

### Setup Steps:

1. **Install dependencies:**
   ```bash
   pip install -r requirement.txt
   ```

2. **Add your user to the input group:**
   ```bash
   sudo usermod -a -G input $USER
   ```

3. **Log out and log back in** (or reboot) for the group change to take effect.

4. **Verify group membership:**
   ```bash
   groups | grep input
   ```
   You should see `input` in the list.

5. **Run baguette:**
   ```bash
   python3 main.py
   ```

### Troubleshooting

**If you see "No keyboard devices found":**
- Make sure you're in the `input` group (see step 2-4 above)
- Check that keyboard devices exist: `ls -l /dev/input/event*`
- You may need to log out and back in after adding yourself to the group

**Security Note:**
Adding yourself to the `input` group allows the application to read keyboard input from all applications. This is necessary for global keyboard shortcuts but means the application has access to all keyboard input. Only run trusted applications with this permission.

## For X11 Users

On X11, baguette uses `pynput` which works out of the box without special permissions.

Just install dependencies and run:
```bash
pip install -r requirement.txt
python3 main.py
```

## Checking Your Display Server

To check if you're using Wayland or X11:
```bash
echo $XDG_SESSION_TYPE
```

- `wayland` = You're using Wayland (follow Wayland instructions above)
- `x11` = You're using X11 (follow X11 instructions above)
