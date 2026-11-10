{config, lib, ...}: let
  aliases = {
    "dv" = "cd ~/Downloads/Video";
    "v" = "nvim";
    "python" = "python3";
    "ta" = "tmux a -t ";
    "dash" = "ta gh && tmux send-keys -t 0 'gh-dash' Enter";
    "dots" = "/usr/bin/git --git-dir=$HOME/.dots/ --work-tree=$HOME";
    "hsf" = "home-manager switch --flake $HOME/.config/home-manager#asyl-omar";
    "dr" = "doppler run -- ";
    "pnsd" = "pnpm start:dev";
    "pnd" = "pnpm dev";
    "pnb" = "pnpm build";
    "pni" = "pnpm install";
    "pna" = "pnpm add";
    "yb" = "yarn build";
    "yd" = "yarn dev";
    "ysd" = "yarn start:dev";
    "uc" = "omarchy update";
    "p8" = "ns -p pnpm_8";
    "d" = "droid";
    "o" = "opencode";
    "cm" = "CLAUDE_CONFIG_DIR=$HOME/.claude claude";
    "mm" = "CLAUDE_CONFIG_DIR=$HOME/.claude-minimax claude";
    "ck" = "CLAUDE_CONFIG_DIR=$HOME/.claude-kimi claude";
    "ccp" = "claude --dangerously-skip-permissions";
  };
in {
  home.file.".zshenv".text = ''
    if [ -r /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh ]; then
      . /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
    fi
    if [ -r "${config.home.profileDirectory}/etc/profile.d/hm-session-vars.sh" ]; then
      . "${config.home.profileDirectory}/etc/profile.d/hm-session-vars.sh"
    fi
  '';

  home.file.".zshrc".text = builtins.readFile ./zshrc + "\n" +
    lib.concatStringsSep "\n" (lib.mapAttrsToList
      (name: value: "alias ${lib.escapeShellArg name}=${lib.escapeShellArg value}") aliases);
}
