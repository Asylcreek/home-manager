# Coder Linux profile

The `coder` flake output uses `home.nix` and targets Debian x86-64 with the `coder` account at `/home/coder`.

Included: Zsh, the Kali Oh My Posh theme, completion, autosuggestions, syntax highlighting, fzf, zoxide, Git/gh-dash, lazygit, tmux with resurrect/continuum, agent instructions, and Claude instructions. Neovim and mise are supplied by the Coder VM image.

Apply changes inside a workspace:

```sh
home-manager switch --flake "path:$HOME/.config/home-manager#coder"
```

Fresh Coder workspaces pull the `linux` branch on first start. Existing workspaces
need a pull and the switch command above. Shared configuration changes belong in
`home.nix`; Linux does not require a separate home module.
