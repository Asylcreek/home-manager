{
  programs.fzf = {
    enable = true;

    enableZshIntegration = true;

    defaultCommand = "fd --strip-cwd-prefix";

    defaultOptions = [
      "--height 40%"
      "--layout=reverse"
      "--border"
      "--inline-info"
    ];
  };
}
