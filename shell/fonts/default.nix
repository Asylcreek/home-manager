{ pkgs, ... }:

{
  home.packages = with pkgs; [
    iosevka

    # # It is sometimes useful to fine-tune packages, for example, by applying
    # # overrides. You can do that directly here, just don't forget the
    # # parentheses. Maybe you want to install Nerd Fonts with a limited number of
    # # fonts?
    (nerdfonts.override { fonts = [ "FiraCode" ]; })
  ];
}
