#!/usr/bin/env bash
# Bootstrap script for quick restoration on a fresh machine or distro hop.
set -euo pipefail

echo "=========================================="
echo " Starting System Restoration via Chezmoi   "
echo "=========================================="

# 1. Install chezmoi if missing
if ! command -v chezmoi &>/dev/null; then
  echo "==> chezmoi not found. Installing..."
  if command -v pacman &>/dev/null; then
    sudo pacman -S --needed --noconfirm chezmoi
  elif command -v dnf &>/dev/null; then
    sudo dnf install -y chezmoi
  elif command -v apt-get &>/dev/null; then
    sudo apt-get update && sudo apt-get install -y chezmoi
  else
    sh -c "$(curl -fsLS get.chezmoi.io)" -- -b "$HOME/.local/bin"
  fi
fi

# 2. Apply dotfiles
echo "==> Applying dotfiles..."
chezmoi init --apply quantavil

echo "=========================================="
echo "  Dotfiles restored successfully!         "
echo "=========================================="
echo ""
echo "If on Arch / CachyOS, you can reinstall your full package set with:"
echo "  sudo pacman -S --needed - < ~/.local/share/chezmoi/pkglist-pacman.txt"
if [ -f "$HOME/.local/share/chezmoi/pkglist-aur.txt" ]; then
  echo "AUR packages:"
  echo "  cat ~/.local/share/chezmoi/pkglist-aur.txt"
fi
