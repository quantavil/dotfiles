# AGENTS.md

Guidance for work in this home directory: CachyOS with Niri + DankMaterialShell (DMS), managed with chezmoi and shared by a desktop PC and a laptop.

This is the single shared copy: `~/AGENTS.md` is a symlink to `.agents/AGENTS.md` inside the chezmoi source (`~/.local/share/chezmoi`). Edit it here — changes land directly in the repo; commit them with git in the source directory. Always update it after any system, config, service, package or environment change.

## General practice

- Inspect current state before changing it; preserve unrelated user changes.
- Principle: **100% Mirroring by default**. Both machines (Desktop and Laptop) must mimic each other in every config, shell bind, theme, window rule, tool, and script. Never delete or strip a tool or config simply because it is not actively used on the current machine.
- Prefer application settings and supported commands over hand-editing managed/generated files.
- Make the smallest useful change, then validate the affected service or configuration.
- Treat optional or hardware-dependent features as opt-in; keep the system lean and bloat-free.
- Never store passwords or weaken authentication policy to make automation easier.

## Machine parity and strict hardware exceptions

Both systems run **CachyOS with Niri + DankMaterialShell (DMS)**, managed by chezmoi from `quantavil/dotfiles`. All tools, keybindings, fonts, icons, terminal settings, shell configurations, scripts, and behaviors are identical.

### Unified Defaults Across Both Systems (No Machine Split)

The following stacks are **default on both Desktop and Laptop**:
- **Release Tools via Mise**: All tools in `~/.config/mise/config.toml` are unified for both machines: `flutter`, `node`, `pnpm`, `github:openai/codex`, `pipx:cloakbrowser`, `github:vercel-labs/agent-browser`, and the five Craft apps (gridcraft, pdfcraft, photocraft, wordcraft, deckcraft).
- **Signing & Document Tools**: `icegate-sign` (and HYP2003 vendor driver paths), printing stack (`cups`, `hplip`, `sane`), and OBS Studio configurations are shared baselines so plugging peripherals into either machine works out of the box.
- **Android Emulator GPU Mode**: `DITTO_GPU=auto` unified across both machines. The emulator auto-probes the RTX 4060 host GPU on desktop and safely selects compatible rendering on laptop without crashing.
- **Browser Automation Platform**: CloakBrowser pro 155 with `~/.local/bin/cloakbrowser-chrome` wrapper, persistent fingerprint seeds, and dynamic extension loading (`bitwarden`, `violentmonkey`, `ublock-origin-lite` from `~/.local/share/bitwarden-cloak`) unified across both machines. Shared 1-seat concurrent license across machines.

### The Exhaustive Whitelist of Hardware/Physical Exceptions

Only the following physical hardware differences are permitted to differ:

1. **GPU & Graphics Drivers**:
   - **Desktop**: Intel i5-12400F (no iGPU) + Nvidia GeForce RTX 4060 (`nvidia-open`, `nvidia-utils`, `opencl-nvidia`, `lib32-nvidia-utils`).
   - **Laptop**: Intel UHD integrated graphics (`mesa`, `intel-media-driver` for VAAPI, no Nvidia drivers).
2. **Displays & Backlight**:
   - **Desktop**: External LG ULTRAGEAR 1920x1080@144Hz on HDMI-A-2 (no sysfs backlight).
   - **Laptop**: Built-in `eDP-1` display with hardware backlight controls via `/sys/class/backlight`. Display outputs are managed per-machine by DMS-generated `dms/outputs.kdl`.
3. **Power & DMS Bar Widgets**:
   - **Desktop**: Wall AC power only (no battery in `/sys/class/power_supply/`). DMS bar has **no battery widget**. Network preference is `networkPreference: wired`.
   - **Laptop**: Battery powered. DMS bar **includes the battery widget** and monitors power via `power-profiles-daemon`. Network preference is `networkPreference: wifi`.

## Dotfiles and Git workflow rules (Mandatory for all agents)

- **Always Sync Before Work**: Before starting any dotfile edits or creating commits, run `git pull --rebase` or `chezmoi update` to integrate remote changes cleanly and prevent divergence.
- **Encapsulate Differences in Templates, Never Delete**: Any machine-specific difference MUST be placed inside Go templates (`{{ if eq .role "desktop" }}` / `{{ if eq .role "laptop" }}` in `.tmpl` files). Never `git rm` or strip shared tools, scripts, environment variables, or packages just because they are not currently active on the machine you are currently working on.
- **Machine Role Detection**: Machine role is determined strictly by hardware (`cat /sys/class/dmi/id/chassis_type`: 3 = desktop, 9/10 = laptop; `ls /sys/class/power_supply/`: no `BAT*` = desktop; `lspci | grep -qi nvidia` = desktop). Each machine keeps an untracked `~/.config/chezmoi/chezmoi.toml` with `[data] role = "desktop"` or `"laptop"`. Never check or branch on hostname.
- **Deliberate Package List Maintenance**: Never run automatic hooks or commands that dump `pacman -Qqe` into `pkglist-pacman.txt` or `pkglist-aur.txt`. Package lists are maintained deliberately for packages that belong in the system baseline.
- **Intentional Drift (Do Not Commit)**: App-generated runtime state must NOT be committed or modified: `.config/kdeglobals`, `.config/shelly/settings.json`, and `.config/DankMaterialShell/*.json`.
- **Validation**: After every dotfile change, run `niri validate -c ~/.config/niri/config.kdl` and `dms doctor -j` to verify both syntax validity and runtime health.

## Desktop session (Niri + DMS)

- Niri config: `~/.config/niri/config.kdl`. Everything under `~/.config/niri/dms/` is generated by DMS — change DMS settings or add includes/overrides to the main config instead. User binds placed after DMS includes override defaults; keep obsolete shell/lock commands out, and lock via the DMS lock interface.
- Greeter / Display Manager: `greetd` + `dux-greeter-bin` (AUR, prebuilt; provides the `dms-greeter` binary — the old `greetd-dms-greeter-bin` no longer exists in the AUR) runs the login screen via Niri on **both** machines (`/etc/greetd/config.toml`, `/etc/greetd/niri/config.kdl` + generated `niri/dms.kdl`); SDDM stays installed but disabled as a fallback. Set up with `dms-greeter install -y`, then `dms-greeter sync`; the greeter user needs the `video` group for `/dev/dri`. PAM for DMS session locking is synced at `/etc/pam.d/dankshell` (`dms auth sync`). Themes and settings stay synced with `dms-greeter sync`. These are system files in `/etc`, not chezmoi-managed — applying dotfiles does not touch the login screen.
- Custom binds: `Mod+B` default browser, `Mod+E` Nautilus (files), `Mod+Z` VS Code, `Shift+Print` regional OCR (`~/.local/bin/dms-ocr`), `Mod+Alt+C` DMS color picker, `Mod+Shift+E` power menu (replaces the session-exit default).
- The CachyOS `dux-shell` package provides `dms-shell`; the shell runs as `dms.service`; use DMS IPC for shell features and settings. Keyboard auto-detection needs `libinput-tools`.
- Window rules: opaque by default; one `window-rule` adds `opacity 0.88` + blur for Rio, Nautilus, Baobab, File Roller, pavucontrol and `com.danklinux.dms` — add further translucent apps there. Global `blur { passes 1 offset 1.0 }`; image viewers (Loupe), browsers, editors, and OBS windows stay fully opaque.

## Theme, fonts, environment

- Qt platform theme: `xdgdesktopportal` (`~/.config/environment.d/90-dms.conf` + Niri environment block). DMS writes `~/.config/qt6ct/qt6ct.conf` on theme changes; apply via DMS, then reopen affected apps.
- Icons: `BeautyLine`; fonts: `MesloLGS Nerd Font` — configured for both Qt (`~/.config/qt6ct/qt6ct.conf`) and GTK/GNOME (`gsettings org.gnome.desktop.interface`).
- Session variables belong in `~/.config/environment.d/90-dms.conf` and Niri's `environment` block; a new login session is required after changing them. System locale: `en_IN.UTF-8` (`/etc/locale.conf`).
- `vim` stays installed (`cachyos-zsh-config` requires it) but `vim.desktop` is masked in `~/.local/share/applications/`.

## Core apps, files, terminals, defaults

- File Manager: Nautilus (GNOME Files). Features: `sushi` (Spacebar media previews), `nautilus-open-any-terminal` (opens Rio via `Ctrl+Alt+T`), `nautilus-admin-gtk4` (admin actions), and `~/.local/bin/nautilus` wrapper (auto-restores last visited directory tracked via `~/.local/share/nautilus-python/extensions/remember_last_dir.py`). A `nautilus-python` extension adds **Print…** for local PDFs via `~/.local/bin/nautilus-print-pdf` and the GTK print dialog; restart Files after extension changes.
- Terminal: Rio via `~/.config/kdeglobals [General]` (`TerminalApplication=rio`, `TerminalService=rio.desktop`) + `~/.config/xdg-terminals.list`; `~/.config/rio/config.toml` uses MesloLGS Nerd Font Mono and `opacity = 1.0` + `unfocused-split-opacity = 1.0` so Niri alone controls translucency.
- Editor: Ferrite (`ferrite-bin` from AUR) for Markdown, structured formats (JSON/YAML/TOML) and general text/code files, exported as `EDITOR`/`VISUAL`. VS Code for `.ipynb`/`.code-workspace` (`com.microsoft.VSCode.desktop`).
- Web browser: Zen (`zen-browser-bin`, `zen.desktop`) is the system default on both machines and the only browser on the laptop; `~/.local/bin/default-browser` (Mod+B) follows `xdg-settings get default-web-browser` and falls back to Zen. The desktop also has `chromium` (cachyos-extra-v3, Wayland auto) and CloakBrowser — both registered MIME handlers for http/https/html, never the default. `cloakbrowser.desktop` (chezmoi-managed) runs the mise-managed stealth build with `--user-data-dir=~/.config/cloakbrowser` and a persisted `--fingerprint` seed. Vivaldi was uninstalled with its profile data — do not reintroduce a role split.
- Media & Utilities: Audio → Amberol (`io.bassi.Amberol.desktop`); Downloads → Prism (`Prism.desktop`); Images → Loupe (`org.gnome.Loupe.desktop`); Task Manager → Mission Center (`io.missioncenter.MissionCenter.desktop`); Archives → File Roller GUI + `ouch` CLI; Disk Usage → Baobab GUI; Script dialogs → `gum` (TUI) & `zenity` (GUI); Network/Code analysis → Sniffnet GUI, `tokei` CLI; Office/PDF/Creative → craft suite (Gridcraft, Wordcraft, Photocraft, Deckcraft, PdfCraft).
- Shell config is fish-only (`~/.config/fish/`); `.bashrc`/`.zshrc` are not managed (fish is the login shell). MIME defaults come from `.chezmoiscripts/run_onchange_after_50-mime-defaults.sh.tmpl`, which sets only installed apps and discovers scheme handlers (Telegram `userapp-*`, chatgpt) at runtime. Inspect with `gio info <file> | grep content-type` / `xdg-mime query default <type>`, set one with `xdg-mime default`; `~/.config/mimeapps.list` itself is app-generated, never commit it.

## Services and integrations

- Manage user components with systemd user services; inspect first (`systemctl --user status`, `journalctl --user -u <unit>`; `journalctl -k` for device/filesystem/firewall issues).
- DankSearch backs DMS filesystem search (`dsearch index status`, `dsearch.service`).
- Firewall: UFW, default-drop incoming; only narrow rules for features in use. Open: MicYou `8554/tcp` (control), `8555/udp` (audio), `8443/tcp` (web). Clients must target host's current DHCP address — never hardcode host IPs in device profiles.
- Phone & LAN transfer: LocalSend for peer-to-peer file transfer.
- MCP servers: centralized in `~/Documents/my-mcps`, deployed by `bun run deploy` to Antigravity, OpenCode, Codex, Cursor, Claude Desktop and Claude Code. The running Claude Desktop app can write back a stale `~/.config/Claude/claude_desktop_config.json`; after deploy, verify its `mcpServers` keys. Active entries: `filesystem`, `fetch`, `memory`, `github` (needs token), `firecrawl`, `context7`, `codebase-memory`, `dart`, `rea` (reverse engineering evidence: binaries, JS/Electron, .NET, APKs, firmware, captures, ADB), `icegate` (`bunx github:quantavil/icegate-mcp`; own repo, source in `~/Documents/icegate-mcp`: ICEGATE public enquiries, import duty, exchange rates, CODES, GSTIN). Deployed entries are prefixed `managed-`.
- Skills: managed in `~/Documents/my-skills` (`bun index.ts` or `./run.sh <command>`: add/remove/sync/set/superskill/enable/disable/status/deploy/doctor/check). `skills.json` is committed; `superskills/` is generated; `.active/` + `skills.local.json` are per machine. Deploy installs symlinks for all agent targets; Gemini/OpenCode read `.active/`, so disabled skills stay hidden. Upstream skills come from the pinned `skills` devDependency — never a floating `bunx`. List current skills with `bun index.ts status`.
- SMB (desktop): `DESKTOP-CNRKSBM` is at `desktop-cnrksbm.local` (192.168.1.5), shares `E`, `Users`; Nautilus accesses on-demand via `smb://desktop-cnrksbm.local/` (`gvfs-smb`, mounts under `/run/user/1000/gvfs/`).
- Printing/scanning (desktop): HP LaserJet Pro MFP M125nw on USB + HP LaserJet 1020 on `DESKTOP-CNRKSBM`; both need the proprietary `hplip-plugin`; stack = `cups`/`cups-filters`/`hplip`, `sane`/`sane-airscan`, GNOME Document Scanner (`simple-scan`; Skanpage removed). HP Scan and HP Device Manager launchers are hidden because they are bundled in the required `hplip` package (USB queue uses `printer-error-policy=retry-job` to prevent CUPS from pausing on device wake delays).

## Privileged operations

- Packages: `pacman` (official/CachyOS) first, `shelly` for AUR. Prefer prebuilt binaries; ask explicit permission for even small source builds. Group related changes into one transaction; verify exact devices/packages/paths/commands before requesting authentication.
- Use `pkexec` with an absolute executable path — no general root shell. Do not weaken sudoers/Polkit, enable NOPASSWD, store passwords, or create persistent elevated helpers.
- Headless agents: `pkexec` via the DMS polkit agent works for short, already-verified root work, but its authorization expires quickly. For long `pacman` runs use a mode-700 `SUDO_ASKPASS` helper under `/tmp/opencode` and `shred -u` it afterwards. `shelly` elevates through `sudo` and fails without a TTY — for scripted runs use `pacman` directly (a PATH shim that only prepends `-A` to sudo works for shelly if needed).
- `checkupdates` syncs its own database copy and can report stale results; confirm with `pacman -Syu`.

## Development tooling

- Browser automation: mise manages `pipx:cloakbrowser` and native `github:vercel-labs/agent-browser`. The free GitHub key is stored locally at `~/.cloakbrowser/license.key` (never commit it); sign in and run `cloakbrowser install` on each machine. The free tier allows one concurrent browser. `~/.local/bin/cloakbrowser-chrome` launches the newest installed licensed browser and keeps a seed per profile; agent-browser uses it in headed mode, and `cloakbrowser.desktop` exposes it as a GUI browser (own profile, stable seed). `CHROME_PATH` and `ARCHIFY_CHROME` also point to the wrapper. `cloakbrowser update` refreshes the browser; do not run `agent-browser install`, which downloads a second Chrome. Without a key `install` serves only the public v146 build; a free key from https://cloakbrowser.dev/free (emailed after GitHub sign-in, stored by `cloakbrowser login`) unlocks the newest pro build (currently 155.0.8059.39.1, 1 concurrent seat) with Ed25519 + SHA-256 verified download. The binary enforces that seat at launch — `Sessions: 1/1 in use` makes it exit 76/PROTOCOL, and a seat leaked by a SIGKILLed browser clears server-side in ~4 minutes; close windows normally. The mise postinstall helper fetches version-matched agent-browser skills. Agent-browser doctor may test a separate Playwright-cached browser; verify the actual process. On the laptop, system chromium and the agent-browser Chrome for Testing cache were removed; Playwright cache remains.
- CloakBrowser (laptop): the personal profile is `~/.config/agent-browser/profiles/personal`; unpacked Bitwarden, Violentmonkey and uBlock Origin Lite are in `~/.local/share/cloak-extensions/`, with `~/.local/share/bitwarden-cloak/` as a compatibility symlink. Keep the profile and login data local; do not delete or reset it without the user’s request.
- ICEGATE draft automation: Google Apps Script project “ICEGATE shipment drafts” checks new ICEGATE LEO/eGatepass mail every minute, processing 10:00–22:00 Asia/Kolkata. It prepares Gmail reply drafts for review, checks for identical files already sent in the selected conversation, and never sends mail. Source and local tests live in `~/Documents/icegate-drafts` (public repo `quantavil/icegate-drafts`, MIT); a time-driven Apps Script trigger runs `checkIcegate`. The script uses Gmail full-access and external-request permissions; do not store credentials in dotfiles.
- ICEGATE DSC: Hypersecu HYP2003 USB token `2ccf:080a` (Feitian ePass2003 family, `ENTERSAFE-ESPK` card layout that OpenSC cannot read), used on Linux through the vendor PKCS#11 library `libcastle_v2.so.1.0.0` (`~/Documents/hyp2003-linux-driver/`, proprietary, local only). The old Wine/nCode flow (prefix `~/.local/share/icegate-wine`, its backup and winetricks cache, HyperPKI/batch-signer launchers, `~/Documents/ICEGATE-HyperPKI-Linux`, the VM fallback with QEMU/swtpm, the custom pcscd reader list under `/etc` and `/usr/local/lib/icegate-ccid`, and the nCode installer zip) was removed once `icegate-sign` was accepted by ICEGATE. The `wine`/`winetricks` packages remain installed. Never store the token PIN; never pass physical Windows partitions to a VM.
- `icegate-sign` (own repo `~/Documents/icegate-sign`, Python/uv, installed with `uv tool install ~/Documents/icegate-sign`, remove with `uv tool uninstall icegate-sign`; not yet published): Linux-native replacement for the Wine/nCode flow above. `icegate-sign doctor|certs|sign|verify`; signs BE/SB/TXT/XML (ICEGATE Text/XML format: SHA-1 DigestInfo over the SHA-256 of the trimmed file, tags appended — XML gets no XMLDSig) and PDFs (pyHanko, one detached CMS signature per page, compact box 5,8,185,52, name and date only) through a PKCS#11 module: the vendor `libcastle_v2.so.1.0.0` in `~/.local/lib/hyp2003/` or `~/Documents/hyp2003-linux-driver/` (proprietary, local only, not a repo; OpenSC cannot read this card: it uses Feitian ENTERSAFE-ESPK, not PKCS#15), falling back to OpenSC. Format was reverse engineered from `nCodePkiComponentV4.jar` and ICEGATE's `pkicomp.js` and checked against the official utility's real output; real-token PDF signing is verified with pdfsig and ICEGATE accepted a file signed this way (user-reported, 2026-10-27); `--pin-stdin` allows non-interactive signing; signed text/XML on a real token is still unverified. First real test: sign one `.be` and compare byte for byte with the old flow. Keep the Wine flow until then. Details in that repo's `AGENTS.md`.
- mise owns release-managed tools (`~/.config/mise/config.toml`): the five crafts (gridcraft, pdfcraft, wordcraft, photocraft, deckcraft — GitHub Linux x86_64 tarballs, release-age-exempt), Codex CLI, Flutter, Node, and pnpm on both systems. `mise-upgrade.timer` runs `mise -C %h -y upgrade` daily; do not add other update engines. `~/.local/libexec/mise-craft-integrate` links craft launchers/icons/MIME via mise `latest` aliases (state: `~/.local/state/mise-craft/links.json`); validate with `mise ls`, the helper's `--check`, and `systemd-analyze --user verify`.
- Codex CLI: mise-managed on both machines (`github:openai/codex`). Resolves through mise shims (`mise activate` in `~/.config/fish/conf.d/10-mise.fish`) ahead of `/usr/bin`.
- Android: user-owned SDK `~/Android/Sdk` (`emulator`/`avdmanager` symlinked into `~/.local/bin`; `sdkmanager` there is an exec wrapper, since a symlink breaks its SDK-root detection; adb from `/usr/bin`). Start emulators as transient units (`systemd-run --user --collect --unit=ditto-emulator -- emulator -avd …`); target serials explicitly and don't share a device between two controllers during captures. The `ditto` skill's `scripts/download-play-apks.sh` pulls the installed delivery from the signed-in x86_64 AVD and rejects 32-bit native APKs.

## Known pitfalls

- Android emulator root (Ditto): Play images refuse `adb root`; root them with rootAVD + current Magisk (rootAVD's bundled Magisk is old: its `su` rejected adb outright). `su: request rejected (2000)` in `logcat -s Magisk` with no prompt means Shell is switched off in Magisk › Superuser; switch it on. Magisk "Direct install" cannot update an emulator; re-patch the ramdisk with rootAVD instead. Snapshots taken before patching are invalid; cold-boot with `-no-snapshot-load`.
- "Something went wrong. Check that Google Play is enabled…" in an app = Play automatic integrity protection; the app only runs on a Play image. Never patch the APK to get past it.
- Android SDK command-line tools resolve the SDK root from their own path: launch `sdkmanager` through an exec wrapper, not a symlink.
- Network symlinks in `$HOME`: Never place symlinks pointing to network CIFS/NFS mounts directly inside `~` (e.g. `~/Windows-E -> /mnt/win_e`). Doing so causes GUI file managers to trigger kernel network probe timeouts on every directory listing when the host is asleep. Access remote shares via `smb://` in bookmarks or Network locations instead.
- Dux Greeter status lies from a non-root shell: `/etc/greetd/config.toml` is mode 600 root-only and `/var/cache/dms-greeter` is `greeter`-group, so `dms-greeter status` reports "Greeter config not found" and "symlink not found" purely on permission errors — check with `sudo dms-greeter status` (expects `/root` paths there, so read the symlinks directly) or after re-login. Group membership added by `dms-greeter sync` only applies to new sessions.
- Never run `dms-greeter install`/`sync` through `pkexec`: it resolves `$HOME` as `/root`, so the cache symlinks and per-user slot get linked to root's state. Run `sudo dms-greeter sync` as yourself (or `sudo -u <user> env HOME=/home/<user> dms-greeter sync`) and `dms-greeter sync --profile` for the per-user slot; remove a stray `/var/cache/dms-greeter/users/root`.
- Chromium (desktop, Nvidia/Wayland) logs one `'--ozone-platform=wayland' is not compatible with Vulkan` error per launch and continues on GL — harmless. If rendering ever breaks, put `--disable-features=Vulkan` in `~/.config/chromium-flags.conf`; that file is honoured by the packaged launcher (verified).
- ISP IPv6 routing timeouts: ISP Wi-Fi (Airtel) can issue IPv6 routes with severe latency and packet loss causing curl, mise, and uv to time out against dual-stack endpoints (like pypi.org). Keep IPv4 precedence configured in `/etc/gai.conf` (`precedence ::ffff:0:0/96 100`).

## Storage and recovery

- Before repairs: identify the filesystem and read kernel logs; prefer a read-only mount when consistency is uncertain; confirm the exact unmounted device before running repair tools; never format as a repair step. Check drive health on I/O errors. `ntfsfix` is limited recovery — recommend a Windows `chkdsk` follow-up. Mount removable storage through UDisks and eject cleanly.

## Validation

- `niri validate -c ~/.config/niri/config.kdl`; `dms doctor -j` plus DMS IPC status; `journalctl --user -u <service>`; `journalctl -k`. After changes, confirm both configuration validity and the actual runtime state.
