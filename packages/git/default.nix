{pkgs,...}:

{
  home.packages = with pkgs; [
    gh
    lazygit
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
  };

  programs.gh-dash = {
    enable = true;
    settings = {
      prSections = [
        { title = "My Pull Requests"; filters = "is:open author:@me"; }
        { title = "Needs My Review"; filters = "is:open review-requested:@me"; }
        { title = "Involved"; filters = "is:open involves:@me -author:@me"; }
      ];

      issuesSections = [
        { title = "My Issues"; filters = "is:open author:@me"; }
        { title = "Assigned"; filters = "is:open assignee:@me"; }
        { title = "My Issues"; filters = "is:open involves:@me -author:@me"; }
      ];

      defaults = {
          preview = {
             open= true;
             width = 50; 
          }; 

          prsLimit = 20;
          issuesLimit = 20;
          view = "prs";
          
          layout = {
            prs = {
              updatedAt = {
                width = 7;
              };
              repo = {
                width = 15;
              };
              author = {
                width = 15;
              };
              assignees = {
                width = 20;
                hidden = true;
              };
              base = {
                width = 15;
                hidden = true;
              };
              lines = {
                width = 16;
              };
            };
            issues = {
              updatedAt = {
                width = 7;
              };
              repo = {
                width = 15;
              };
              creator = {
                width = 10;
              };
              assignees = {
                width = 20;
                hidden = true;
              };
            };
          };

          refetchIntervalMinutes = 30;
      };

      keybindings = {
         issues = [
            { key = "e"; command = "tmux display-popup -d {{.RepoPath}} -w 80% -h 90% -E 'nvim -c \":Octo issue edit {{.IssueNumber}}\"'"; }
            { key = "i"; command = "tmux display-popup -d {{.RepoPath}} -w 80% -h 90% -E 'nvim -c \":Octo issue create\""; }
           ];

           prs = [
            { key = "O"; command = "tmux new-window -c {{.RepoPath}} 'gh pr checkout {{ .PrNumber }} && nvim fun.txt -c \":Octo pr edit {{.PrNumber}}\""; }
           ];
      };

      repoPaths = {
        "deelaa-marketplace/eticketing-frontend" = "~/Documents/deelaa/customer";
        "GATE-Acad/assignmenthelp-frontend" = "~/Documents/GATE/assignmenthelp-frontend";
        "GATE-Acad/assignmenthelp-backend" = "~/Documents/GATE/assignmenthelp-backend";
        "GATE-Acad/GATE-Academy-Client" = "~/Documents/GATE/site";
        "GATE-Acad/gate-admin" = "~/Documents/GATE/admin";
        "GATE-Acad/gate-dashboard" = "~/Documents/GATE/dashboard";
        "GATE-Academy/gate-api" = "~/Documents/GATE/api";
      };

      theme = {
        ui = {
          table = {
            showSeparator = true;
          };
        };
      };

      pager = {
        diff = "";
      };
    };
  };
}
