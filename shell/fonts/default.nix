{ pkgs, ... }:

{
  home.packages = with pkgs; [
    iosevka
    maple-mono.variable
  ];
}
