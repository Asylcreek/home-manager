{ config, lib, ... }: {
  home.activation.installMiseTools = lib.hm.dag.entryBetween [ "reloadSystemd" ] [ "linkAgents" ] ''
    (
      cd "$HOME"
      run /usr/local/bin/mise install
    )
  '';

  systemd.user.services.t3code = {
    Unit.Description = "T3 Code server";
    Service = {
      ExecStart = "${config.home.homeDirectory}/.local/share/mise/shims/t3 serve --port 3773";
      Environment = [
        "T3CODE_HOST=127.0.0.1"
        "PATH=${config.home.homeDirectory}/.local/share/mise/shims:${config.home.homeDirectory}/.nix-profile/bin:${config.home.homeDirectory}/.local/bin:/usr/local/bin:/usr/bin:/bin"
      ];
      EnvironmentFile = "-%h/.config/t3code/service.env";
      WorkingDirectory = config.home.homeDirectory;
      Restart = "on-failure";
      RestartSec = 5;
    };
    Install.WantedBy = [ "default.target" ];
  };

  systemd.user.startServices = "sd-switch";
}
