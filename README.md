# Dotfiles (`quantavil`)

Personal dotfiles managed with [chezmoi](https://www.chezmoi.io/).

## Quick Restore (Fresh Install / Distro Hop)

Since this is a **public repository**, you can immediately initialize and apply your environment on any machine without authenticating first:

### Method 1: Using Chezmoi (Recommended)
```bash
sudo pacman -S --needed chezmoi
chezmoi init --apply quantavil
```

### Method 2: Single-line curl installer (No pacman needed first)
```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply quantavil
```

### Reinstalling System Packages (Arch / CachyOS)
```bash
# Official packages
sudo pacman -S --needed - < ~/.local/share/chezmoi/pkglist-pacman.txt

# AUR packages
cat ~/.local/share/chezmoi/pkglist-aur.txt
```

---

## Daily Workflow

- **Check for local changes:**
  ```bash
  chezmoi diff
  ```
- **Add or re-add a config:**
  ```bash
  chezmoi add ~/.config/<path>
  ```
- **Commit and push updates:**
  ```bash
  chezmoi cd
  git add .
  git commit -m "update configs"
  git push
  ```
  *(Note: Package lists `pkglist-pacman.txt` and `pkglist-aur.txt` are automatically refreshed on every commit via pre-commit hook).*
- **Pull latest changes from GitHub:**
  ```bash
  chezmoi update
  ```

---

## What's Included

- **Compositor:** Niri (`~/.config/niri/config.kdl`) — catch-all glass (`opacity 0.88` + minimal blur) with opaque exclusions for media/PiP/browsers/focus apps/auth dialogs
- **Default terminal:** Rio (`~/.config/rio/config.toml`, MesloLGS Nerd Font Mono, opacity delegated to Niri); Alacritty config also tracked
- **Shells:** Fish, Zsh, Bash
- **Shell Extensions & Themes:** DankMaterialShell settings & plugins
- **Desktop & Theme Integration:** BeautyLine icons (KDE + Qt + GTK), MesloLGS Nerd Font (Qt + GTK), Qt6ct (`qt6ct.conf`), KDE globals, XDG user dirs, `environment.d`, `xdg-terminals.list`
- **Shims & Utilities:** `~/.local/bin/` (`default-browser`, `zedit`, `dms-ocr`)
- **App Defaults:** Zed editor settings, MIME associations (`mimeapps.list`), MPV, Navi, Shelly
- **Documentation & Rules:** `AGENTS.md`
- **Package Manifests:** `pkglist-pacman.txt`, `pkglist-aur.txt` (auto-synced)

## Mise release tools

`~/.config/mise/config.toml` is the single tool inventory. Add a GitHub release
with `mise use -g github:OWNER/REPO@latest` (some repositories need asset/layout
options). Run `mise upgrade` to upgrade all configured tools, or
`mise upgrade --dry-run` to check. Version ranges and exact pins are respected.

The enabled `mise-upgrade.timer` runs the same unfiltered upgrade command daily
from the home directory. Future globally configured tools are included;
project-only configuration elsewhere is outside this timer's scope.
The desktop helper refreshes the four existing Craft apps' menu/icon integration;
it does not download or choose updates. Other GUI apps may need separate desktop
integration.

After applying these dotfiles and installing the system package manifest:

```bash
mise -C "$HOME" install
systemctl --user daemon-reload
systemctl --user start mise-upgrade.service
systemctl --user enable --now mise-upgrade.timer
```

Only configuration, units and the integration helper are tracked. Mise downloads,
extracted binaries, generated desktop links/caches and integration state are not
copied into the repository. The previous tar updater and app-specific update
tasks/wrappers are retired.
