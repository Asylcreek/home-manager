# Proxmox host profile

The `proxmox` branch provides one standalone Home Manager profile for the `root`
account at `/root` on x86-64 Debian-based Proxmox hosts. The flake output is
`proxmox`; all hosts use the same configuration.

Home Manager manages Zsh, the Kali Oh My Posh prompt, completion, autosuggestions,
syntax highlighting, fzf, zoxide, Git configuration, and tmux with
resurrect/continuum. Nix supplies Neovim, its Tree-sitter CLI and C compiler
prerequisites, the shell tools, fd, and ripgrep. Git uses the host's APT-managed
binary. `EDITOR` and the `v` alias both use `nvim`.

The profile does not change `/etc/passwd`, Bash configuration, Proxmox services,
networking, storage, or APT packages. Set the login shell separately after
activation. The prompt shows the username and hostname so hosts remain
distinguishable.

Coder's T3 service, mise installation, agent configuration, GitHub CLI/dashboard,
and development aliases are not activated by this profile.

## Install on a host

Install [Nix in multi-user mode](https://nix.dev/manual/nix/latest/installation/installing-binary.html#multi-user-installation)
and [standalone Home Manager](https://nix-community.github.io/home-manager/)
first. Enable `nix-command` and `flakes` in the Nix configuration. Git must be
available from the host. Run the following as `root`.

Once the branch has been published:

```sh
git clone --branch proxmox https://github.com/Asylcreek/home-manager.git ~/.config/home-manager
cd ~/.config/home-manager
nix build --no-link '.#homeConfigurations.proxmox.activationPackage'
home-manager switch -b before-home-manager --flake "path:$HOME/.config/home-manager#proxmox"
```

The first switch backs up conflicting dotfiles with the `.before-home-manager`
suffix. Review any existing `~/.zshrc`, `~/.zshenv`, `~/.zprofile`, Git config,
and tmux config before switching. Try one host first, then test a fresh SSH
session and tmux before applying to the others.

## Root login shell

After activation, install Debian's Zsh and change root's login shell:

```sh
apt-get install --no-install-recommends zsh
chsh -s /usr/bin/zsh root
```

The system binary keeps login access independent of the Nix profile. Home
Manager supplies its configuration and Nix profile paths. Keep an existing SSH
session open while testing a new login. Remote SSH commands now run through
Zsh; invoke `/bin/bash` explicitly for commands that require Bash syntax.

## Update

```sh
cd ~/.config/home-manager
git pull --ff-only
home-manager switch --flake "path:$HOME/.config/home-manager#proxmox"
```

The `hsf` alias runs the switch command inside Zsh. It does not pull Git changes
or update the flake lock. The existing lock file is retained from `coder`.

## Roll back

Use `home-manager generations` to find the previous generation and run its
`activate` script. Before uninstalling Home Manager or Nix, restore the login
shell with `chsh -s /bin/bash root`. Then use `home-manager uninstall` and restore
the backed-up dotfiles. These operations do not roll back Proxmox or APT changes.
