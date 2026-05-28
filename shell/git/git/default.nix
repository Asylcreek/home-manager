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

   includes = [
      {
        contents = {
          user = {
            email = "omokugbo.b@turing.com";
            name = "Omokugbo Boro";
          };
        };

        condition = "gitdir:~/Documents/turing/";
      }
   ];

   ignores = [
      # macOS
      ".DS_Store"
      "._*"
      ".Spotlight-V100"
      ".Trashes"

      # envs
      ".env"
      ".env*"
      "!.env.example"
      ".envrc"
      ".direnv/"

      ".claude"
      ".opencode"
      ".codex"
      ".factory"
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
}
