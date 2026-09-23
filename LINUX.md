# Coder Linux profile

The `coder` flake output targets Debian x86-64 and `/home/coder`. It reuses the shell modules and selected dotfiles without loading the macOS home profile or a global `.env`.

Included: Zsh, the Kali Oh My Posh theme, completion, autosuggestions, syntax highlighting, fzf, zoxide, Git/gh-dash, lazygit, tmux with resurrect/continuum, agent instructions, and Claude instructions. Neovim and mise are supplied by the Coder VM image.

Apply changes inside a workspace:

```sh
home-manager switch --flake "path:$HOME/.config/home-manager#coder"
```

For an optional project GitHub token, create `.env` in that project:

```dotenv
GH_TOKEN=your_project_token
```

Put `dotenv` in `.envrc`, then run `direnv allow`. The Zsh hook loads the variables on directory entry and unloads them on exit. Both files are ignored by the shared Git configuration. No token is stored in the template or base image.

The Coder image embeds a snapshot of this branch. Updating the repository files inside an existing VM and running Home Manager changes that VM; rebuilding the base image supplies the change to new VMs.
