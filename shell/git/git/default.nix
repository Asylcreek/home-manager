{...}: {
  programs.git = {
    enable = true;
    # Keep the host's APT-managed Git binary.
    package = null;

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
}
