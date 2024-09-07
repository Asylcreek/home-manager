{pkgs,...}:

{
  home.packages = with pkgs; [
    gh
    lazygit
    diff-so-fancy
  ];

  programs.git = {
   enable = true;
   
   userName = "Omokugbo Joseph Boro";
   userEmail = "omokugbobr@gmail.com";

   extraConfig = {
     init = {
       defaultBranch = "main";
      };
   };

   ignores = [
        # macOS
        ".DS_Store"
        "._*"
        ".Spotlight-V100"
        ".Trashes"
    ];

    diff-so-fancy = {
      enable = true;
    };
  };

}
