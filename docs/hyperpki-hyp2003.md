# Hypersecu HYP2003 token on CachyOS

This is the opt-in Wine setup used for the Hypersecu HYP2003 token (USB ID `2ccf:080a`). The token manager and certificate login were checked with Wine 10 and reported working after upgrading the desktop to Wine 11.20. The pre-upgrade prefix backup is `~/.local/share/icegate-wine-before-wine11`. A PDF signature was verified in an experimental Wine 11.20 signer session; ICEGATE eSanchit acceptance remains unverified.

## Set up another machine

1. Apply these dotfiles on the laptop with chezmoi. The `hyperpki-setup` and `hyperpki-token-manager` commands and app-menu launcher come from the dotfiles; the Wine installation and the reader's system configuration are created separately on each machine.
2. Install the dependencies on CachyOS using the normal package update procedure, for example `sudo pacman -Syu --needed wine winetricks pcsclite ccid pcsc-tools`. Follow the machine's normal authentication process. On another Arch-based distribution, the Wine package name may differ.
3. Plug in the token. In Files, open its built-in `HyperPKI_230719` drive and locate `HyperPKI_HYP2003_Setup.exe`. Do not use an installer from an untrusted site.
4. Run the setup command, replacing the example path with the actual installer path. Quote the path if it contains spaces:

   ```sh
   hyperpki-setup '/run/media/quantavil/HyperPKI_230719/HyperPKI_HYP2003_Setup.exe'
   ```

   The command creates an isolated Wine prefix, installs the token manager and its `mfc42` dependency, configures the CCID reader, and enables the PC/SC socket. It requests system authentication via `pkexec`; no password or token PIN is saved. If the installer drive is not mounted, open it in Files first. Internet access is needed by Winetricks.
5. Open **HyperPKI Token Manager** from the app menu, or run `hyperpki-token-manager`. With the token connected, log in with its PIN and check that your certificate appears. Never export the private key.

The setup uses a copy of the packaged CCID reader list, with the token's USB ID added, at `/usr/local/lib/icegate-ccid/ifd-ccid.bundle/Contents/Info.plist`. Its driver library is a symlink to the packaged library. A systemd drop-in points `pcscd` at that list. If `ccid` is upgraded, refresh the list from the new package with:

```sh
hyperpki-setup --reader-only
```

To check reader detection, run `pcsc_scan -r`; it should show `Hypersecu HYP2003`. If not, check that the token is plugged in and run `systemctl status pcscd.socket pcscd.service` and `journalctl -u pcscd.service`.

For eSanchit, the certificate must be registered to the ICEGATE user, and the upload flow must still be tested. This setup does not install Windows or a VM.

The token manager may keep running after its window closes; check with `pgrep -af HyperPKITokenManager`.

A temporary desktop test ran the official nCode signer in a network namespace with `pasta` outbound access and `socat` forwarding to loopback only. A dedicated Chromium session temporarily allowed the bundled localhost certificate's public-key hash. The ICEGATE signing page produced a token-signed PDF; `pdfsig` reported a valid signature covering the whole document, but its local issuer trust check failed. ICEGATE eSanchit acceptance and a reusable signer launcher remain untested. No CA root certificate was installed or trusted for this test.
