# AGENTS.md

Guidance for AI agents operating on CachyOS (Niri + DankMaterialShell), managed via chezmoi (`quantavil/dotfiles`) across two mirrored machines: Desktop and Laptop.

`~/AGENTS.md` symlinks to `.agents/AGENTS.md` in the chezmoi source (`~/.local/share/chezmoi`). Commit changes here.

---

## 1. Core Operating Principles

- **100% Mirroring**: Both machines share configs, keybinds, themes, window rules, tools, and scripts. Never delete or unmanage a tool because it is inactive on the current machine.
- **Always Pre-Sync**: `git pull --rebase` or `chezmoi update` before any dotfile edit.
- **Templates Over Deletion**: Machine differences go in Go templates (`.tmpl`, `{{ if eq .role "desktop" }}`). Never `git rm` shared tools. The only allowed `.role` uses are `networkPreference` and the battery widget in `dot_config/DankMaterialShell/settings.json.tmpl`; anything else optional is gated on presence (`stat`), never role. Audit with `grep -rn '\.role' ~/.local/share/chezmoi --exclude-dir=.git`.
- **Role Detection**: Hardware only, never hostname. Desktop = chassis type 3, no `BAT*` in `/sys/class/power_supply/`, Nvidia GPU (`lspci | grep -qi nvidia`). Laptop = chassis 9/10, `BAT*` present, Intel iGPU only. Stored as `[data] role` in untracked `~/.config/chezmoi/chezmoi.toml`.
- **Package Sync**: The chezmoi lists are the source of truth: `pkglist-pacman.txt`, `pkglist-aur.txt`, `pkglist-flatpak.txt`, hardware lists (`pkglist-gpu-nvidia.txt`, `pkglist-intel-igpu.txt`), and `pkglist-removed.txt` (tombstones). Install → add to the matching list. Uninstall → delete from its list **and** tombstone it so the other machine removes it. Commit and push in the same task. `run_onchange_after_55-pkg-sync` applies lists on `chezmoi update` (root via `pkexec`, AUR via `shelly`); only tombstoned names are ever removed. `pkg-sync --dry-run` previews, `pkg-sync --audit` shows installed-but-unlisted drift (never auto-write lists). Never auto-generate lists via hooks. Prune tombstones once both machines have applied them.
- **Untracked Runtime Drift**: Never commit or alter app-generated state: `.config/kdeglobals`, `.config/shelly/settings.json`, and DMS JSON other than `settings.json.tmpl`. `chezmoi diff` noise here is expected; never `chezmoi apply` them blindly.

---

## 2. Hardware Exceptions (Only Permitted Differences)

| Component | Desktop | Laptop | Handling |
|---|---|---|---|
| **GPU** | Nvidia RTX 4060 (`nvidia-open`, `nvidia-utils`, `opencl-nvidia`) | Intel UHD (`mesa`, `intel-media-driver` for VAAPI) | `pkg-sync` picks the Nvidia/iGPU list from `lspci`; `pkglist-pacman.txt` is shared |
| **Display** | External LG 1080p@144Hz on `HDMI-A-2`, no sysfs backlight | Built-in `eDP-1` with `/sys/class/backlight` | DMS auto-generates `dms/outputs.kdl` |
| **Power/Network** | AC only, `networkPreference: wired`, no battery widget | Battery, `networkPreference: wifi`, battery widget | Templated in `settings.json.tmpl` |

---

## 3. Desktop Session (Niri + DMS)

- **Compositor**: Niri (`~/.config/niri/config.kdl`). `~/.config/niri/dms/` is generated — never hand-edit; user overrides go at the bottom of `config.kdl`.
- **Window Rules**: Opaque by default; `opacity 0.88` + blur for Rio, Nautilus, Baobab, File Roller, pavucontrol, and DMS. Browsers, Loupe, editors, and OBS stay 100% opaque.
- **Login**: `greetd` + `dux-greeter-bin` (`dms-greeter`) on Niri (`/etc/greetd/config.toml`, `/etc/greetd/niri/`). Sync with `sudo -u <user> env HOME=/home/<user> dms-greeter sync`, never via `pkexec`. Lock via DMS (PAM `/etc/pam.d/dankshell`).
- **Keybinds**: `Mod+B` browser · `Mod+E` Nautilus · `Mod+Z` VS Code · `Shift+Print` OCR (`~/.local/bin/dms-ocr`) · `Mod+Alt+C` DMS color picker · `Mod+Shift+E` power menu.

---

## 4. System Defaults

- **Shell/Terminal**: Fish (`~/.config/fish/`, user binaries via `conf.d/05-local-bin.fish`); Rio (`~/.config/rio/config.toml`, MesloLGS Nerd Font Mono, opacity handled by Niri).
- **Apps**: Zen (`zen-browser-bin`) is the browser; CloakBrowser is the automation browser. Micro is `EDITOR`/`VISUAL`; VS Code for `.ipynb`/`.code-workspace` and code projects. Amberol audio, Loupe images, MPV video. Nautilus, Mission Center, Baobab, File Roller. Craft suite (Gridcraft, Wordcraft, Photocraft, Deckcraft, PdfCraft).
- **Environment/Theme**: `~/.config/environment.d/90-dms.conf` + Niri `environment` block (relogin required). BeautyLine icons, MesloLGS Nerd Font, Qt platform `xdgdesktopportal` (`qt6ct.conf` from DMS).

---

## 5. Development Tools & Runtimes

- **Mise** (`~/.config/mise/config.toml`): `flutter`, `node`, `pnpm`, `github:openai/codex`, `pipx:cloakbrowser`, `github:vercel-labs/agent-browser` (skills sync hook), Craft suite (5 apps). Updates daily via `mise-upgrade.timer`.
- **Browser Automation (CloakBrowser Pro 156)**: wrapper `~/.local/bin/cloakbrowser-chrome` runs the pro build with a persistent fingerprint seed. Free pro tier has **1 concurrent seat** shared by both machines; close sessions cleanly (a leaked seat clears in ~4 min). **Rule**: drive browsers only through `agent-browser` with its profile (`~/Documents/ALWAYS-USE-PROFILE`); never launch a browser binary directly (headless included) or with another `--user-data-dir`. Tell subagents the same; they must report failure instead of falling back. Run `agent-browser close` when finished. `~/.agent-browser/config.json` uses `cloakbrowser-chrome`, `--fingerprint-platform=windows`, and loads Bitwarden/Violentmonkey/uBlock Lite from `~/.local/share/bitwarden-cloak/` only when present.
- **Android**: SDK at `~/Android/Sdk` (`adb` in `/usr/bin`, `emulator` in `~/.local/bin`, `sdkmanager` wrapper). `DITTO_GPU=auto` on both machines. Run with `systemd-run --user --collect --unit=ditto-emulator -- emulator -avd <name> ...`.
- **ICEGATE Signing** (`icegate-sign`): repo `~/Documents/icegate-sign`, installed via `uv tool install ~/Documents/icegate-sign`. Signs BE, SB, TXT, XML, and PDF with the HYP2003 token (`2ccf:080a`) and vendor lib `libcastle_v2.so.1.0.0` in `~/.local/lib/hyp2003/`. `run_once_after_60-hyp2003-driver.sh` verifies `SHA256SUMS` and copies it only if absent; the vendor binary is never committed.
- **ICEGATE Drafts**: Apps Script in `~/Documents/icegate-drafts` (`quantavil/icegate-drafts`, MIT). Trigger `checkIcegate` scans SB/BoE LEO/eGatepass mail every minute, 11:00–22:00 Asia/Kolkata, and prepares Gmail reply drafts on the latest non-draft message; skips files already sent, never sends. No credentials in dotfiles.
- **MCPs & Skills**: MCPs from `~/Documents/my-mcps/mcp-servers.json`, deployed with `./run.sh deploy`. Every enabled server loads directly in all agents; never pin versions (`pkg@latest`). Gortex (code graph, `gortex` from mise): in large repos, search with it before reading files; `gortex track <repo>` once per project; never run `gortex install`/`init`. Skills from `~/Documents/my-skills/bundles.json`: each entry is a whole upstream repo (never a subset) or a local skill in `skills/`. `./run.sh sync && ./run.sh deploy` (`vendor/` is per machine, untracked). `tier: core` links into every agent; `tier: gateway` only through `find-skill`, so check it before saying no skill exists.

---

## 6. Critical Pitfalls

- **Privilege Elevation**: `pkexec` with full binary paths for short interactive actions; mode-700 `SUDO_ASKPASS` under `/tmp/opencode` for long headless pacman runs. Never NOPASSWD or weaker Polkit.
- **Dux Greeter**: never `pkexec dms-greeter` (`$HOME` resolves to `/root` and breaks the cache).
- **No Network Symlinks in `$HOME`**: no symlinks to CIFS/NFS mounts in `~` (e.g. `~/Windows-E`); use `smb://` in GVfs/Nautilus, or sleeping hosts freeze the kernel.
- **IPv6**: Airtel IPv6 drops packets to PyPI/curl; keep IPv4 precedence in `/etc/gai.conf` (`precedence ::ffff:0:0/96 100`).
- **Ozone Warning**: `'--ozone-platform=wayland' is not compatible with Vulkan` on Nvidia is harmless; GL fallback is normal.

---

## 7. Validation

After any system or config change:

```bash
niri validate -c ~/.config/niri/config.kdl
dms doctor -j
systemctl --user status <affected-service>
```
