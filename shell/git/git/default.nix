{pkgs,...}:

{
  home.packages = with pkgs; [
    gh
  ];

  programs.git = {
   enable = true;
   
   userName = "Omokugbo Joseph Boro";
   userEmail = "omokugbobr@gmail.com";

   extraConfig = {
     init = {
       defaultBranch = "main";
      };

     merge.conflictStyle = "zdiff3";
   };

   ignores = [
        # macOS
        ".DS_Store"
        "._*"
        ".Spotlight-V100"
        ".Trashes"
   ];

   delta = {
      enable = true;

      options = {
        navigate = true;
        dark = true;
        line-numbers = true;
        hyperlinks = true;
      };
   };
  };

  programs.lazygit = {
    enable = true;

    settings = {
      git.paging = {
        colorArg = "always";
        pager = "delta --dark --paging=never --line-numbers --hyperlinks --hyperlinks-file-link-format=lazygit-edit://{path}:{line}";
      };
    };
  };
}
