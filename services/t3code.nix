{ lib, ... }: {
  programs.zsh.envExtra = lib.mkAfter ''
    # Coder shells may bypass PAM even while the systemd user manager is running.
    if [[ -z "$XDG_RUNTIME_DIR" && -d "/run/user/$(id -u)" ]]; then
      export XDG_RUNTIME_DIR="/run/user/$(id -u)"
    fi
    if [[ -z "$DBUS_SESSION_BUS_ADDRESS" && -S "$XDG_RUNTIME_DIR/bus" ]]; then
      export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
    fi
  '';

  home.activation.installMiseTools = lib.hm.dag.entryBetween [ "reloadSystemd" ] [ "linkAgents" ] ''
    (
      cd "$HOME"
      run /usr/local/bin/mise install
    )
  '';

  systemd.user.startServices = "sd-switch";
}
