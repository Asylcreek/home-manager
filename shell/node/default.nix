{ pkgs, ... }:

{
  home.packages = with pkgs; [
    # prevent installing node with pnpm
    (pnpm_8.overrideAttrs
      (oldAttrs: rec {
        buildInputs = [ ];
      }))

    # prevent installing node with yarn
    (yarn.override { nodejs = null; })
  ];
}

