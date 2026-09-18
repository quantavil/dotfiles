# Dotfiles (`quantavil`)

Personal dotfiles managed with [chezmoi](https://www.chezmoi.io/).

## Quick Restore (Fresh Install / Distro Hop)

Since this is a **private repository**, authenticate GitHub first, then let chezmoi clone and apply your environment:

### Method 1: Using GitHub CLI (`gh`) - Recommended
```bash
# 1. Authenticate with GitHub
gh auth login

# 2. Initialize and apply dotfiles in one command
chezmoi init --apply quantavil
```

### Method 2: Using SSH
```bash
chezmoi init --apply git@github.com:quantavil/dotfiles.git
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
