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
- **Package Sync (agent workflow)**: Lists in the chezmoi source are the source of truth: `pkglist-pacman.txt`, `pkglist-aur.txt`, `pkglist-flatpak.txt`, hardware lists (`pkglist-gpu-nvidia.txt`, `pkglist-intel-igpu.txt`), and `pkglist-removed.txt` (tombstones). When you install an app or package for the user, add it to the matching list; when you uninstall one, delete it from its list **and** add it to `pkglist-removed.txt` so the other machine removes it too. Commit and push in the same task. `run_onchange_after_55-pkg-sync` applies lists on `chezmoi update` (root via `pkexec`, AUR via `shelly`). Only tombstoned names are ever removed. `pkg-sync --dry-run` previews; `pkg-sync --audit` shows installed-but-unlisted drift to review (never auto-write lists). Tombstone entries may be pruned once both machines have applied them.
- **No Role Branching Elsewhere**: The only `.role` uses allowed are `networkPreference` and the battery widget in `dot_config/DankMaterialShell/settings.json.tmpl`. Anything optional that exists on only one machine is gated on presence (`stat`), never on role. Check with `grep -rn '\.role' ~/.local/share/chezmoi --exclude-dir=.git`.
- **Untracked Runtime Drift**: Do not commit or alter app-generated runtime state: `.config/kdeglobals`, `.config/shelly/settings.json`, and DMS JSON other than the templated `settings.json.tmpl`. `chezmoi diff` noise on these is expected; never `chezmoi apply` them blindly.

---

## 2. Hardware Exceptions (Only Permitted Differences)

Only three physical hardware realities differ between machines:

| Component | Desktop (`desktop`) | Laptop (`laptop`) | Handling |
|---|---|---|---|
| **GPU & Drivers** | Intel i5-12400F + Nvidia RTX 4060 (`nvidia-open`, `nvidia-utils`, `opencl-nvidia`). | Intel UHD graphics (`mesa`, `intel-media-driver` for VAAPI). | `pkg-sync` picks `pkglist-gpu-nvidia.txt` / `pkglist-intel-igpu.txt` from `lspci`; `pkglist-pacman.txt` is shared. |
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
  - Agent Browser: `~/.agent-browser/config.json` uses `cloakbrowser-chrome`, `--fingerprint-platform=windows`, and loads unpacked extensions (`bitwarden`, `violentmonkey`, `ublock-origin-lite` from `~/.local/share/bitwarden-cloak/`) only when that directory exists (presence-gated, untracked data; missing on desktop until copied over).
- **Android SDK & Emulators**:
  - SDK root: `~/Android/Sdk` (`adb` in `/usr/bin`, `emulator` in `~/.local/bin`, `sdkmanager` via exec wrapper).
  - Emulator GPU mode: `DITTO_GPU=auto` unified on both machines (auto-probes RTX 4060 on desktop; selects safe fallback on laptop).
  - Run transient units: `systemd-run --user --collect --unit=ditto-emulator -- emulator -avd <name> ...`
- **ICEGATE Digital Signing (`icegate-sign`)**:
  - Repo: `~/Documents/icegate-sign` (installed via `uv tool install ~/Documents/icegate-sign`).
  - Supports: BE, SB, TXT, XML, and PDF signing via HYP2003 USB token (`2ccf:080a`) using vendor driver `libcastle_v2.so.1.0.0` (in `~/.local/lib/hyp2003/` or `~/Documents/hyp2003-linux-driver/`).
  - Driver provisioning: `.chezmoiscripts/run_once_after_60-hyp2003-driver.sh` clones `quantavil/hyp2003-linux-driver` (HTTPS), verifies `SHA256SUMS`, and copies the library to `~/.local/lib/hyp2003/` only if absent. The vendor binary is never committed to dotfiles.
- **ICEGATE Shipment Drafts**:
  - Google Apps Script automation in `~/Documents/icegate-drafts` (public `quantavil/icegate-drafts`, MIT). Time-driven Apps Script trigger `checkIcegate` scans new LEO/eGatepass mail every minute, processing 11:00–22:00 Asia/Kolkata. Prepares Gmail reply drafts on the latest non-draft message, skips files already sent in the thread, never sends. Uses Gmail full-access + external-request scopes; store no credentials in dotfiles.
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
