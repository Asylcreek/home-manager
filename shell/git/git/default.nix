{pkgs, ...}: {
  home.packages = with pkgs; [
    gh
  ];

  programs.git = {
    enable = true;

    settings = {
      init = {
        defaultBranch = "main";
      };

      merge.conflictStyle = "zdiff3";

      user = {
        email = "omokugbobr@gmail.com";
        name = "Omokugbo Joseph Boro";
      };
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

  };

  programs.delta = {
    enable = true;
    enableGitIntegration = true;

    options = {
      navigate = true;
      dark = true;
      line-numbers = true;
      hyperlinks = true;
    };
  };
}
