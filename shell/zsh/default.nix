{ pkgs, ... }:

{
  home.packages = with pkgs; [
    oh-my-posh
  ];

  programs.zsh = {
    enable = true;

    autosuggestion = {
      enable = true;
    };

    enableCompletion = true;

    plugins = [
      {
        name = "vi-mode";
        src = pkgs.zsh-vi-mode;
        file = "share/zsh-vi-mode/zsh-vi-mode.plugin.zsh";
      }
    ];

    oh-my-zsh = {
      enable = true;
      plugins = [ "git" ];
      theme = "";
    };

    shellAliases = {
      "dv" = "cd ~/Downloads/Video";
      "vlc" = "/Applications/VLC.app/Contents/MacOS/VLC";
      "vim" = "nvim";
      "python" = "python3";
      "ta" = "tmux a -t ";
      "dash" = "ta gh && tmux send-keys -t 0 'gh dash' Enter";
      "dots" = "/usr/bin/git --git-dir=$HOME/.dots/ --work-tree=$HOME";
      "edng" = "vim ~/Library/Application\ Support/ngrok/ngrok.yml";
    };

    syntaxHighlighting = {
      enable = true;
    };

    history = {
      expireDuplicatesFirst = true;
      ignorePatterns = [ "doppler*" ];
      ignoreAllDups = true;
    };

    initExtra = ''
      # oh-my-posh
      # possible options: emodipt-extend, kali, pure, negligible, craver, honukai, wopian
      eval "$(oh-my-posh init zsh --config $HOME/.nix-profile/share/oh-my-posh/themes/wopian.omp.json)"

      # fnm
      eval "$(fnm env --use-on-cd --resolve-engines)" 
    '';
  };

}
