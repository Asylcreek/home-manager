{ config, pkgs, ... }:

{
  home.packages = with pkgs; [
    ffmpegthumbnailer
    poppler
  ];
  
  programs.yazi = {
    enable = true;
    enableZshIntegration = true;
    initLua = ./init.lua;
    plugins = {
      "relative-motions.yazi" = ./plugins/relative-motions.yazi;
    };
    keymap = {
      manager.prepend_keymap = [
        { on = [ "1" ]; run = "plugin relative-motions --args=1"; desc = "Move in relative steps"; }
        { on = [ "1" ]; run = "plugin relative-motions --args=1"; desc = "Move in relative steps"; }
        { on = [ "2" ]; run = "plugin relative-motions --args=2"; desc = "Move in relative steps"; }
        { on = [ "3" ]; run = "plugin relative-motions --args=3"; desc = "Move in relative steps"; }
        { on = [ "4" ]; run = "plugin relative-motions --args=4"; desc = "Move in relative steps"; }
        { on = [ "5" ]; run = "plugin relative-motions --args=5"; desc = "Move in relative steps"; }
        { on = [ "6" ]; run = "plugin relative-motions --args=6"; desc = "Move in relative steps"; }
        { on = [ "7" ]; run = "plugin relative-motions --args=7"; desc = "Move in relative steps"; }
        { on = [ "8" ]; run = "plugin relative-motions --args=8"; desc = "Move in relative steps"; }
        { on = [ "9" ]; run = "plugin relative-motions --args=9"; desc = "Move in relative steps"; }
      ];
    };
  };
}
