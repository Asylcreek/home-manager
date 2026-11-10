# Omarchy dotfiles

Home Manager manages personal configuration for `asyl` on `asyl-omar`.
Omarchy and Arch's package tools install applications. Linuxbrew is not used.
The target is `x86_64-linux` with home directory `/home/asyl`; Home Manager
does not change the machine's hostname or login shell.

## Setup

Install Nix with flakes enabled, then clone the `omarchy` branch at
`~/.config/home-manager`. Install the applications below through Omarchy's
package installation interface or Arch's package tools before using their
configuration. No application installation happens during Home Manager activation.

From the repository directory:

```sh
nix build .#homeConfigurations.asyl-omar.activationPackage
./result/activate
```

For later changes:

```sh
home-manager switch --flake ~/.config/home-manager#asyl-omar
```

The only application added to the Nix profile is Home Manager itself. Its
activation/build dependencies still live in the Nix store. System Python at
`/usr/bin/python3` is required for the Claude MCP configuration merge.

## What comes from book

| Configuration | What is retained |
| --- | --- |
| Zsh | Portable aliases, history, completion preferences, Oh My Zsh Git plugin, autosuggestions, highlighting, Ghostty shell integration |
| Prompt | Oh My Posh themes and the existing `kali.omp.json` selection, including Nix-shell context |
| Shell tools | fzf options, fd search command, zoxide's `c` command, mise and direnv hooks |
| tmux | Prefix `C-,`, keybindings, pane navigation/resizing, status bar, history, resurrect and continuum settings |
| Git | Both identities, directory-specific identity, ignore rules, delta pager, GitHub credential helper |
| gh-dash | PR/issue sections, layout, keybindings, pager, repository paths |
| mise / lazygit | Existing configuration, with lazygit using standard delta hyperlinks |
| Agents | Latest shared instructions, skills, commands, agent definitions, named Codex agents, Claude settings/statusline/MCP, Codex settings, OpenCode settings |

The tmux module stays in `shell/tmux`, and reads `dots/tmux/tmux.conf`.
`gh-dash` is invoked directly, so it does not require a separate `gh dash`
extension installation. Repository paths under `~/Documents` are retained;
clone projects there or update the paths for this machine.

## Applications and plugins

Install what you need from this list through Omarchy/Arch. Some may already
be installed by Omarchy. AUR package availability and names can change.

| Purpose | Arch/AUR packages |
| --- | --- |
| Shell | `zsh`, `zsh-autocomplete`, `zsh-autosuggestions`, `zsh-syntax-highlighting`, `oh-my-zsh-git` |
| Prompt | `oh-my-posh` |
| Shell integration | `fzf`, `fd`, `zoxide`, `carapace`, `direnv`, `mise` |
| Git and dashboard | `git`, `github-cli`, `git-delta`, `gh-dash`, `diff-so-fancy` |
| Terminal sessions | `tmux`, `tmux-plugin-manager` |
| Editor / activation | `neovim`, `python` |

Optional Zsh integrations load only when installed. The Oh My Zsh package is
expected at `/usr/share/oh-my-zsh`; Zsh plugins are expected under
`/usr/share/zsh/plugins`. To try the shell, run `/usr/bin/zsh` or configure
your terminal to launch it. Omarchy's Bash configuration remains untouched.

TPM is loaded from `/usr/share/tmux-plugin-manager/tpm`, the path provided by
the AUR package. In tmux, press `C-,` then uppercase `I` to install resurrect
and continuum. TPM manages these plugins, not Nix.

The `uc` alias runs `omarchy update`. It does not update Nix or Home Manager.
The existing mise configuration declares runtime/tool versions; mise downloads
those when you install them. Install AI clients such as Claude, Codex and
OpenCode separately. API keys and account state are not deployed by this repo.

## File ownership and boundaries

Home Manager generates Zsh, Git, gh, gh-dash and tmux configuration. Other
managed files and agent directories link back to this checkout so applications
can update mutable settings. Back up existing configuration before the first
activation; Home Manager stops on conflicting unmanaged files rather than
forcefully replacing them.

Claude MCP servers are merged into `~/.claude.json`, preserving account and
other settings. Existing server definitions with the same names are replaced
by the repository's definitions. Provide `KANEO_API_KEY` and other credentials
separately through your environment.

Omarchy keeps control of the desktop, terminal configuration and themes.
AeroSpace, Ibudo, and the Apple-oriented Kanata configuration are not activated.
Yazi, font and Node Nix modules were already disabled on `book` and remain
unimported. Local `.env` and `.envrc` files are not copied into the Nix store;
Zsh still reads an existing `~/.env`.

## Verification

Evaluate the target without activating it:

```sh
nix eval .#homeConfigurations.asyl-omar.activationPackage.drvPath --raw
nix eval --json .#homeConfigurations.asyl-omar.config.home.packages \
  --apply 'packages: map (p: p.pname or p.name) packages'
```

The package list should contain only `home-manager` and `hm-session-vars.sh`.
Linux activation and the installed Omarchy application's behavior must still be
checked on `asyl-omar`.
