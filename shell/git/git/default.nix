{...}: {
  programs.git = {
    enable = true;
    package = null;

    settings = {
      init = {
        defaultBranch = "main";
      };

      merge.conflictStyle = "zdiff3";
      core.pager = "delta";
      pager.blame = "delta";
      interactive.diffFilter = "delta --color-only";
      delta = {
        navigate = true;
        dark = true;
        line-numbers = true;
        hyperlinks = true;
      };
      credential."https://github.com".helper = ["" "!gh auth git-credential"];
      credential."https://gist.github.com".helper = ["" "!gh auth git-credential"];

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

      "cspell.json"

      "mise.local.toml"

      ".agents"
      ".claude"
      ".opencode"
      ".codex"
      ".factory"
      ".context"
    ];
  };

  xdg.configFile."gh/config.yml".text = ''
    git_protocol: https
    editor: nvim
    prompt: enabled
  '';
}
