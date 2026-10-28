# AGENTS.md

Guidance for AI agents operating on CachyOS (Niri + DankMaterialShell), managed via chezmoi (`quantavil/dotfiles`) across two mirrored machines: Desktop and Laptop.

`~/AGENTS.md` is a symlink to `.agents/AGENTS.md` in the chezmoi source (`~/.local/share/chezmoi`). Changes must be committed here.

---

## 1. Core Operating Principles

- **100% Mirroring by Default**: Both machines share identical configs, shell binds, themes, window rules, tools, and scripts. Never delete or unmanage a tool simply because it is not active on the current machine.
- **Always Pre-Sync**: Run `git pull --rebase` or `chezmoi update` before starting any dotfile edits to avoid divergence.
- **Templates Over Deletion**: Encapsulate unavoidable machine differences in Go templates (`{{ if eq .role "desktop" }}` / `{{ if eq .role "laptop" }}` in `.tmpl` files). Never `git rm` shared tools.
- **Role Detection**: Detected strictly via hardware:
  - Desktop (`role = "desktop"`): Chassis type 3 (`cat /sys/class/dmi/id/chassis_type`), no `BAT*` in `/sys/class/power_supply/`, Nvidia GPU present (`lspci | grep -qi nvidia`).
  - Laptop (`role = "laptop"`): Chassis type 9/10, `BAT*` present, Intel iGPU only.
  - Stored in untracked `~/.config/chezmoi/chezmoi.toml` (`[data] role = "..."`). Never branch on hostname.
- **No Package List Dumps**: Never auto-generate `pkglist-*.txt` via hooks. Maintain baseline packages deliberately.
- **Untracked Runtime Drift**: Do not commit or alter app-generated runtime state: `.config/kdeglobals`, `.config/shelly/settings.json`, and `.config/DankMaterialShell/*.json`.

---

## 2. Hardware Exceptions (Only Permitted Differences)

Only three physical hardware realities differ between machines:

| Component | Desktop (`desktop`) | Laptop (`laptop`) | Handling |
|---|---|---|---|
| **GPU & Drivers** | Intel i5-12400F + Nvidia RTX 4060 (`nvidia-open`, `nvidia-utils`, `opencl-nvidia`). | Intel UHD graphics (`mesa`, `intel-media-driver` for VAAPI). | Pacman driver baseline. |
| **Display & Brightness** | External LG 1080p@144Hz on `HDMI-A-2` (no sysfs backlight). | Built-in `eDP-1` with hardware backlight (`/sys/class/backlight`). | DMS auto-generates `dms/outputs.kdl`. |
| **Power & Network** | Wall AC only, `networkPreference: wired`, no battery widget. | Battery powered, `networkPreference: wifi`, battery widget enabled. | Templated in `settings.json.tmpl`. |

---

## 3. Desktop Session (Niri + DMS)

- **Compositor**: Niri (`~/.config/niri/config.kdl`). Modular DMS includes are in `~/.config/niri/dms/` (auto-generated; do not hand-edit). User overrides go at the bottom of `config.kdl`.
- **Window Rules**: Opaque by default. `opacity 0.88` + blur enabled for Rio, Nautilus, Baobab, File Roller, pavucontrol, and DMS. Browsers, image viewers (Loupe), editors, and OBS remain 100% opaque.
- **Login / DM**: `greetd` + `dux-greeter-bin` (provides `dms-greeter`) on Niri (`/etc/greetd/config.toml`, `/etc/greetd/niri/`). Sync with `sudo -u <user> env HOME=/home/<user> dms-greeter sync`. Lock via DMS interface (PAM at `/etc/pam.d/dankshell`).
- **Core Keybinds**:
  - `Mod+B`: Browser (`default-browser`)
  - `Mod+E`: Files (`nautilus`)
  - `Mod+Z`: VS Code (`code`)
  - `Shift+Print`: OCR (`~/.local/bin/dms-ocr`)
  - `Mod+Alt+C`: DMS color picker
  - `Mod+Shift+E`: Power menu

---

## 4. System Defaults & Environment

- **Shell**: Fish (`~/.config/fish/`). User binaries prepended via `conf.d/05-local-bin.fish`.
- **Terminal**: Rio (`~/.config/rio/config.toml`, MesloLGS Nerd Font Mono, opacity handled by Niri).
- **Default Apps**:
  - Browser: Zen (`zen-browser-bin`) default on both. Secondary: `chromium` and `cloakbrowser`.
  - Editor: Ferrite (`ferrite-bin`, CLI/GUI `EDITOR`/`VISUAL`); VS Code for `.ipynb`/`.code-workspace`.
  - Media: Amberol (Audio), Loupe (Images), MPV (Video).
  - Utilities: Nautilus (GNOME Files), Mission Center (Task Manager), Baobab (Disk Usage), File Roller (Archives).
  - Office/Creative: Craft suite (Gridcraft, Wordcraft, Photocraft, Deckcraft, PdfCraft).
- **Environment**: Set in `~/.config/environment.d/90-dms.conf` and Niri's `environment` block. Requires relogin.
- **Theme**: BeautyLine icons, MesloLGS Nerd Font, Qt platform `xdgdesktopportal` (`qt6ct.conf` written by DMS).

---

## 5. Development Tools & Runtimes

- **Mise (`~/.config/mise/config.toml`)**: Universal tool inventory on both machines:
  - `flutter`, `node`, `pnpm`
  - `github:openai/codex`
  - `pipx:cloakbrowser`
  - `github:vercel-labs/agent-browser` (with skills sync hook)
  - Craft suite (5 apps)
  - Auto-updates daily via `mise-upgrade.timer`.
- **Browser Automation (CloakBrowser Pro 155)**:
  - Executable wrapper: `~/.local/bin/cloakbrowser-chrome` (launches pro build with persistent fingerprint seed).
  - License: Free pro tier with **1 concurrent seat** shared between machines. Close sessions cleanly to release seat (leaked seat clears in ~4 min).
  - Agent Browser: `~/.agent-browser/config.json` uses `cloakbrowser-chrome`, `--fingerprint-platform=windows`, and dynamically loads unpacked extensions (`bitwarden`, `violentmonkey`, `ublock-origin-lite` from `~/.local/share/bitwarden-cloak/`) when present.
- **Android SDK & Emulators**:
  - SDK root: `~/Android/Sdk` (`adb` in `/usr/bin`, `emulator` in `~/.local/bin`, `sdkmanager` via exec wrapper).
  - Emulator GPU mode: `DITTO_GPU=auto` unified on both machines (auto-probes RTX 4060 on desktop; selects safe fallback on laptop).
  - Run transient units: `systemd-run --user --collect --unit=ditto-emulator -- emulator -avd <name> ...`
- **ICEGATE Digital Signing (`icegate-sign`)**:
  - Repo: `~/Documents/icegate-sign` (installed via `uv tool install ~/Documents/icegate-sign`).
  - Supports: BE, SB, TXT, XML, and PDF signing via HYP2003 USB token (`2ccf:080a`) using vendor driver `libcastle_v2.so.1.0.0` (in `~/.local/lib/hyp2003/` or `~/Documents/hyp2003-linux-driver/`).
- **ICEGATE Shipment Drafts**:
  - Google Apps Script automation in `~/Documents/icegate-drafts` (MIT, checks LEO/eGatepass mail 10:00–22:00 IST). Prepares Gmail drafts; never sends.
- **MCP Servers & Skills**:
  - Centralized in `~/Documents/my-mcps`, deployed via `bun run deploy`.
  - Skills in `~/Documents/my-skills`, managed via `./run.sh <command>`.

---

## 6. Critical Pitfalls & Privileged Operations

- **Privilege Elevation**: Use `pkexec` with full binary paths for short interactive actions; use mode-700 `SUDO_ASKPASS` under `/tmp/opencode` for long headless pacman commands. Never enable NOPASSWD or weaken Polkit.
- **Dux Greeter Sync**: Never run `dms-greeter` through `pkexec` (resolves `$HOME` to `/root` and breaks cache). Run `sudo -u <user> env HOME=/home/<user> dms-greeter sync`.
- **No Network Symlinks in `$HOME`**: Never place symlinks to CIFS/NFS mounts directly in `~` (e.g., `~/Windows-E -> /mnt/win_e`). Access remote shares via `smb://` in GVfs/Nautilus to prevent kernel freeze timeouts when hosts sleep.
- **IPv6 Latency / Timeouts**: Airtel IPv6 routes can drop packets to PyPI/curl. Keep IPv4 precedence in `/etc/gai.conf` (`precedence ::ffff:0:0/96 100`).
- **Chromium Ozone Warning**: Harmless `'--ozone-platform=wayland' is not compatible with Vulkan` on Nvidia; fallback to GL is normal.

---

## 7. Validation Checklist

After any system or config change, run:
```bash
niri validate -c ~/.config/niri/config.kdl
dms doctor -j
systemctl --user status <affected-service>
```
