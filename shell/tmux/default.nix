{ config, pkgs, ... }:

{
  programs.tmux = {
    enable = true;

    clock24 = true;

    escapeTime = 0;

    extraConfig = ''
      # Enable vim motions in view mode
      set-window-option -g mode-keys vi

      set-option -g default-terminal "screen-256color"
      set-option -g focus-events on

      bind-key -T copy-mode-vi 'v' send -X begin-selection # start selecting text with "v"
      bind-key -T copy-mode-vi 'y' send -X copy-selection # copy text with "y"

      unbind -T copy-mode-vi MouseDragEnd1Pane # don't exit copy mode when dragging with mouse

      # Smart pane switching with awareness of Neovim splits.
      bind-key -n C-h if -F "#{@pane-is-vim}" 'send-keys C-h'  'select-pane -L'
      bind-key -n C-j if -F "#{@pane-is-vim}" 'send-keys C-j'  'select-pane -D'
      bind-key -n C-k if -F "#{@pane-is-vim}" 'send-keys C-k'  'select-pane -U'
      bind-key -n C-l if -F "#{@pane-is-vim}" 'send-keys C-l'  'select-pane -R'

      # Smart pane resizing with awareness of Neovim splits.
      bind-key -n M-h if -F "#{@pane-is-vim}" 'send-keys M-h' 'resize-pane -L 3'
      bind-key -n M-j if -F "#{@pane-is-vim}" 'send-keys M-j' 'resize-pane -D 3'
      bind-key -n M-k if -F "#{@pane-is-vim}" 'send-keys M-k' 'resize-pane -U 3'
      bind-key -n M-l if -F "#{@pane-is-vim}" 'send-keys M-l' 'resize-pane -R 3'

      tmux_version='$(tmux -V | sed -En "s/^tmux ([0-9]+(.[0-9]+)?).*/\1/p")'
      if-shell -b '[ "$(echo "$tmux_version < 3.0" | bc)" = 1 ]' \
          "bind-key -n 'C-\\' if -F \"#{@pane-is-vim}\" 'send-keys C-\\'  'select-pane -l'"
      if-shell -b '[ "$(echo "$tmux_version >= 3.0" | bc)" = 1 ]' \
          "bind-key -n 'C-\\' if -F \"#{@pane-is-vim}\" 'send-keys C-\\\\'  'select-pane -l'"

      bind-key -T copy-mode-vi 'C-h' select-pane -L
      bind-key -T copy-mode-vi 'C-j' select-pane -D
      bind-key -T copy-mode-vi 'C-k' select-pane -U
      bind-key -T copy-mode-vi 'C-l' select-pane -R
      bind-key -T copy-mode-vi 'C-\' select-pane -l

      set -g allow-passthrough on

      set -ga update-environment TERM
      set -ga update-environment TERM_PROGRAM

      set -g status-right " "

      set -g pane-border-style fg=yellow
      set -g pane-active-border-style 'fg=yellow,bg=yellow'

      #  modes
      setw -g clock-mode-colour yellow
      setw -g mode-style 'fg=black bg=yellow bold'

      # panes
      set -g pane-border-style 'fg=yellow'
      set -g pane-active-border-style 'fg=yellow'

      # statusbar
      set -g status-position bottom
      set -g status-justify left
      set -g status-style 'fg=yellow'

      set -g status-left ' #{?client_prefix,[,}#{session_name}#{?client_prefix,],} '
      # set -g status-left-style 'fg=black bg=yellow'
      set -g status-left-length 20

      setw -g window-status-current-style 'underscore'
      setw -g window-status-current-format ' #I #W #F '

      setw -g window-status-style 'fg=yellow bg=black'
      setw -g window-status-separator ""
      setw -g window-status-format ' #I #[fg=white]#W #[fg=yellow]#F '

      setw -g window-status-bell-style 'fg=yellow bg=yellow bold'

      # messages
      set -g message-style 'fg=yellow bg=black bold'

      set -g set-titles on
      set -g set-titles-string '#T - #S / #W'
    '';

    historyLimit = 50000;

    keyMode = "vi";

    mouse = true;

    plugins = with pkgs.tmuxPlugins; [
      {
        plugin = resurrect;
        extraConfig = ''
          set -g @resurrect-strategy-vim 'session'
          set -g @resurrect-strategy-nvim 'session'
          set -g @resurrect-capture-pane-contents 'on'
        '';
      }

      {
        plugin = continuum;
        extraConfig = ''
          set -g @continuum-restore 'on'
          set -g @continuum-boot 'off'
          set -g @continuum-save-interval '10'
        '';
      }


    ];

    prefix = "C-,";

    sensibleOnTop = false;

    shell = "${pkgs.zsh}/bin/zsh";

    terminal = "xterm-256color";

    tmuxinator = {
      enable = true;
    };
  };
}
