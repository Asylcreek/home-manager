{ lib, ... }:

{
  imports = [
    ./shell
  ];

  # Home Manager needs a bit of information about you and the paths it should
  # manage.
  home.username = "asyl";
  home.homeDirectory = "/Users/asyl";

  # This value determines the Home Manager release that your configuration is
  # compatible with. This helps avoid breakage when a new Home Manager release
  # introduces backwards incompatible changes.
  #
  # You should not change this value, even if you update Home Manager. If you do
  # want to update the value, then make sure to first check the Home Manager
  # release notes.
  home.stateVersion = "24.05"; # Please read the comment before changing.

  # The home.packages option allows you to install Nix packages into your
  # environment.
  home.packages =  [
    # jq
    # ripgrep
    # fd
    # tor
    # watchman
    # mongosh
    # doppler
    # nowplaying-cli
    # unar
    # tree
    # certbot
    # wget
    #
    # # develop
    # go
    # redis
    # fnm
    # cargo

    # # You can also create simple shell scripts directly inside your
    # # configuration. For example, this adds a command 'my-hello' to your
    # # environment:
    # (pkgs.writeShellScriptBin "my-hello" ''
    #   echo "Hello, ${config.home.username}!"
    # '')
  ];

  # Home Manager is pretty good at managing dotfiles. The primary way to manage
  # plain files is through 'home.file'.
  home.file = {
    # # Building this configuration will create a copy of 'dotfiles/screenrc' in
    # # the Nix store. Activating the configuration will then make '~/.screenrc' a
    # # symlink to the Nix store copy.
    # ".screenrc".source = dotfiles/screenrc;

    # # You can also set the file content immediately.
    # ".gradle/gradle.properties".text = ''
    #   org.gradle.console=verbose
    #   org.gradle.daemon.idletimeout=3600000
    # '';
    ".config/ghostty/config".source = ./dots/ghostty/config;
    ".config/ghostty/themes/jellybeans-muted".source = ./dots/ghostty/themes/jellybeans-muted;
    ".config/ghostty/themes/moonfly".source = ./dots/ghostty/themes/moonfly;
    ".config/ghostty/themes/gruvbox".source = ./dots/ghostty/themes/gruvbox;
    ".config/aerospace/aerospace.toml".source = ./dots/aerospace.toml;
    ".env".source = ./dots/.env;
    ".envrc".source = ./dots/.envrc;
  };

  home.activation.linkAgents = lib.hm.dag.entryAfter ["writeBoundary"] ''
    agentSource="$HOME/.config/home-manager/dots/agents"

    declare -A nameMap=(
      [.factory]="AGENTS.md"
      [.opencode]="AGENTS.md"
      [.claude]="CLAUDE.md"
    )

    declare -A agentsMap=(
      [.factory]="droids"
      [.opencode]="agents"
      [.claude]="agents"
    )

    for target in .factory .opencode .claude; do
      mkdir -p $HOME/$target
      ln -sfn $agentSource/AGENTS.md $HOME/$target/''${nameMap[$target]}
      ln -sfn $agentSource/agents $HOME/$target/''${agentsMap[$target]}
      ln -sfn $agentSource/commands $HOME/$target
      ln -sfn $agentSource/rules $HOME/$target
      ln -sfn $agentSource/skills $HOME/$target
    done

    ln -sfn ~/.config/home-manager/dots/agents/scripts $HOME/.factory
    ln -sfn ~/.config/home-manager/dots/agents/android-bench $HOME/Documents/turing/android-bench/.factory/droids
  '';
  # Home Manager can also manage your environment variables through
  # 'home.sessionVariables'. These will be explicitly sourced when using a
  # shell provided by Home Manager. If you don't want to manage your shell
  # through Home Manager then you have to manually source 'hm-session-vars.sh'
  # located at either
  #
  #  ~/.nix-profile/etc/profile.d/hm-session-vars.sh
  #
  # or
  #
  #  ~/.local/state/nix/profiles/profile/etc/profile.d/hm-session-vars.sh
  #
  # or
  #
  #  /etc/profiles/per-user/asyl/etc/profile.d/hm-session-vars.sh
  #
  home.sessionVariables = {
    # EDITOR = "emacs";
  };

  home.sessionPath = [
    "$HOME/.amp/bin"
  ];

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;

  xdg.enable = true;
}
