---
name: ibudo
description: Control Ibudo workspaces, panes, terminals, SSH sessions, and connected remote Ibudo servers over Ibudo's local Unix sockets without using the GUI.
---

# Ibudo

Use the bundled `scripts/ibudo.py` CLI (stdlib Python 3, located next to this file) to drive Ibudo over its two local Unix sockets. Prefer the default compact text output over `--json` unless you are piping into a parser, so outputs stay small and untruncated.

## Pick the right layer

| Layer | Socket | Needs GUI | Use it for |
| --- | --- | --- | --- |
| Daemon (`IbudoServer`) | `~/Library/Application Support/Ibudo/server/server.sock` | No | Find panes by label/title (`panes`), read or send input to local and managed SSH terminals, run headless shells, reach connected remote Macs (`--server mini`), scan ports, files, SSH profiles, and activity |
| App local control (`Ibudo.app`) | `/tmp/ibudo-<uid>/Ibudo/c.sock` (via `endpoint.json`) | Yes | Inspect live UI focus/split trees (`identify`, `layout`), change workspaces/tabs/splits/focus/titles/sidebars/settings, and launch SSH profile panes in the UI |

Pane IDs vs terminal IDs:
- For local `terminal` panes, `pane:<uuid>` and `terminalID` share the same `<uuid>`.
- For `sshTerminal` panes, `pane:<uuid>` is the UI pane ID, while `server.sock` uses `ssh-<connectionID>` and requires a `managed` `{connectionID, generation}` reference on attach.
- `scripts/ibudo.py panes`, `read`, and `send` handle both automatically: pass `pane:<uuid>`, `<uuid>`, or `ssh-<connectionID>` directly.

Global flags work before or after any subcommand: `--json`, `--namespace IbudoDebug` (or `IBUDO_NAMESPACE`), `--server <name>` (daemon commands), `--socket <path>`, `--timeout <seconds>`.

## Find and read panes (local, SSH, and remote Macs)

Start with `panes` whenever the user refers to a tab or pane by name (including SSH profile names like `mega-prod` whose live terminal title may differ):

```sh
scripts/ibudo.py panes                         # all saved panes joined with live terminals
scripts/ibudo.py panes --filter mega-prod      # filter by profile, label, title, workspace, or ID
scripts/ibudo.py panes --live-only             # only panes with running terminals
scripts/ibudo.py read <pane-or-terminal-id>    # read-only plain screen text, pwd, title, atPrompt
scripts/ibudo.py read <id> --snapshot          # raw ANSI screen + scrollback replay
```

Send input to an existing local or managed SSH terminal:

```sh
# Use --if-idle on SSH panes (remote bash often lacks OSC 133 atPrompt); --if-at-prompt on local zsh
# Avoid raw literal TAB characters in interactive commands (readline treats TAB as completion)
scripts/ibudo.py send <id> "docker ps -a" --enter --if-idle --wait-prompt --capture
```

## Daemon commands (headless, works with `--server <name>`)

Start `IbudoServer` headless if `server.sock` does not exist:

```sh
scripts/ibudo.py ensure
```

Hosts, terminals, and headless runs:

```sh
scripts/ibudo.py servers                       # local Mac + connected remote Ibudo servers
scripts/ibudo.py terminals                     # raw live terminals from server.sock
scripts/ibudo.py --server mini panes           # inspect panes on a connected remote Mac
scripts/ibudo.py run "git status -sb" --cwd /path/to/repo
scripts/ibudo.py spawn --cwd /path/to/repo     # create a persistent headless shell
scripts/ibudo.py terminate <terminal-id>       # kill an ordinary terminal (not managed SSH)
```

Host services (local or `--server <name>`):

```sh
scripts/ibudo.py session                       # read saved session snapshot via session.exchange
scripts/ibudo.py ports                         # TCP listeners + process commands
scripts/ibudo.py activity --limit 20           # Ibudo activity log
scripts/ibudo.py service server.info           # host metadata + advertised methods
scripts/ibudo.py service ssh.profiles.list     # saved SSH profiles
scripts/ibudo.py service files.list '{"root":"/Users/asyl","path":"/Users/asyl"}'
```

## App local control commands (requires running `Ibudo.app`)

Inspect UI state and available actions:

```sh
scripts/ibudo.py identify                      # app_boot_id, context_generation, active handles
scripts/ibudo.py layout                        # windows, workspaces (local + remote), tabs, panes
scripts/ibudo.py context                       # current focus and resolved terminal context
scripts/ibudo.py actions --filter pane         # live catalog of allowlisted actions + schemas
scripts/ibudo.py ssh-profiles                  # SSH profiles + active SSH pane handles
scripts/ibudo.py git-status --tab tab:active   # Git status for a local tab
scripts/ibudo.py search "split"                # command palette search with replayable requests
scripts/ibudo.py settings-get terminal.profile.global.font_size
```

Run allowlisted actions (`ibudo.py action` fetches fresh `app_boot_id`, `context_generation`, and concrete handles automatically):

```sh
scripts/ibudo.py action pane.split_right
scripts/ibudo.py action terminal.new_pane --workspace base --tab <tab-id>
scripts/ibudo.py action pane.rename '{"title":"tests"}' --pane <pane-id>
scripts/ibudo.py action workspace_tab.create
scripts/ibudo.py action ssh.connect_profile '{"profile_id":"<uuid>"}'
scripts/ibudo.py action servers.turn_on '{"server":"mini"}'
scripts/ibudo.py action pane.close --pane <pane-id> --availability
```

Actions that create objects return `data.created_handles` (for example `{"pane": "pane:<uuid>"}`). Pass that handle straight to `read` or `send`.

Confirmations and async operations:
- Destructive actions (`workspace.delete`, closing a busy pane) exit with status 2 and print `confirmation_token` plus `prompt`. Ask the user before re-running with `--confirm <token>`, unless the user explicitly requested the destructive action.
- File transfers (`transfer.start`, `transfer.start_replace`) show an in-app approval sheet and return `operation_id`. Poll with `scripts/ibudo.py op <operation-id> --wait 30`.
- Escape hatch for new or raw intents: `scripts/ibudo.py lc '{"kind":"app.ping"}'`.

## Guardrails

- **Never resize user panes by accident.** Always use `scripts/ibudo.py read` / `send` (which fetch exact `cols` and `rows` from `list` before attaching). If talking to `server.sock` directly, pass the terminal's existing `cols` and `rows` to `attach`.
- **Check before typing into a user's pane.** Use `read <id>` or `--if-at-prompt` before sending input so you do not type into a running editor or TUI. Do not include raw literal TAB characters (`\t`) in interactive shell commands sent via `send` because readline consumes them as completion. Prefer `run`, `spawn`, or `action terminal.new_pane` for local commands.
- **Clean up temporary terminals.** `run` terminates its shell automatically unless `--keep` is passed. Terminate any `spawn` terminals you created when finished unless the user wants them kept.
- **Respect confirmation gates and owner boundaries.** Do not silently bypass `confirmation_required`. Do not attempt `directOwnerGUI`-only host services (`terminal.policy.set`, `storage.status`, `ssh.credentials.*`, `activity.append`/`reclassify`, `servers.*` mutations, `server.sock.protected`); they require `Ibudo.app`'s code signature and return `local_owner_required`.

For wire-level framing, exact `ssh.*` and `session.exchange` schemas, and error codes, read [references/protocol.md](references/protocol.md).
