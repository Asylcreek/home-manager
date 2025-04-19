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

    oh-my-zsh = {
      enable = true;
      plugins = [ "git" ];
      theme = "";
    };

    shellAliases = {
      "dv" = "cd ~/Downloads/Video";
      "vlc" = "/Applications/VLC.app/Contents/MacOS/VLC";
      "v" = "nvim";
      "python" = "python3";
      "ta" = "tmux a -t ";
      "dash" = "ta gh && tmux send-keys -t 0 'gh dash' Enter";
      "dots" = "/usr/bin/git --git-dir=$HOME/.dots/ --work-tree=$HOME";
      "edng" = "v ~/Library/Application\ Support/ngrok/ngrok.yml";
      "hsf" = "darwin-rebuild switch --impure";
    };

    syntaxHighlighting = {
      enable = true;
    };

    history = {
      expireDuplicatesFirst = true;
      ignorePatterns = [ "doppler*" ];
      ignoreAllDups = true;
      extended = true;
    };

    initExtra = ''
      # oh-my-posh
      # possible options: emodipt-extend, kali, pure, negligible, craver, honukai, wopian
      eval "$(oh-my-posh init zsh --config $HOME/.nix-profile/share/oh-my-posh/themes/wopian.omp.json)"

      # fnm
      eval "$(fnm env --use-on-cd --resolve-engines)" 

      # Amazon Q post block. Keep at the bottom of this file.
      [[ -f "$HOME/Library/Application Support/amazon-q/shell/zshrc.post.zsh" ]] && builtin source "$HOME/Library/Application Support/amazon-q/shell/zshrc.post.zsh"
    '';

    initExtraFirst = ''
      # Amazon Q pre block. Keep at the top of this file.
      [[ -f "$HOME/Library/Application Support/amazon-q/shell/zshrc.pre.zsh" ]] && builtin source "$HOME/Library/Application Support/amazon-q/shell/zshrc.pre.zsh"
      '';
  };

}
