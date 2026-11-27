# Ibudo socket protocol reference

Use `scripts/ibudo.py` for normal tasks. Refer to this file when debugging failures, calling raw methods via `service` or `lc`, or updating the skill after Ibudo protocol changes.

## Daemon socket (`server.sock`)

- Path: `~/Library/Application Support/<namespace>/server/server.sock` (`<namespace>` defaults to `Ibudo`; debug uses `IbudoDebug`).
- Framing: newline-delimited UTF-8 JSON (`\n`). Base64 for binary `data` fields.
- Mode selection: the first frame on a connection selects either Terminal protocol v3 (`hello`, `list`, `attach`, `terminate`) or Host services v1 (`{"op":"service","service":{...}}`). A connection cannot switch modes.

### Terminal protocol v3

- `hello`: returns `protocolVersion` (3), `serverPID`, `serverID` (epoch), `build`, `serverOwnedStorage`, `replaced`.
- `list`: returns `terminals[]` with `terminalID`, `backend`, `pid`, `serverPID`, `sequence`, `cols`, `rows`, `busy`, `exited`, `exitCode?`.
- `attach`: `{"op":"attach","backend":"ghostty","terminalID":"...","cols":120,"rows":40}`
  - Ordinary creation flags: `hostDefaults: true` (rejects `environment`, `command`, `managed`), `cwd` (absolute path), `recreate: true` (respawn a `lost` ID), `scrollbackLimit`, `scrollbackLimitLines`.
  - Managed SSH terminals (`terminalID` prefixed `ssh-`): MUST include `"managed":{"connectionID":"<uuid>","generation":"<uuid>"}` and MUST omit `recreate`, `command`, `environment`, `cwd`, and `hostDefaults`. Omitting `managed` returns `managed_attachment_required`. Obtain `connectionID` and `generation` from `session.exchange` `read` (`snapshot.paneTabs[].payload` -> `sshTerminalContext.serverResource`) or from `ssh.connect`'s reply.
  - Attaching to a terminal with 0 active viewers grants `sizeOwner: true` and resizes the PTY to `cols`x`rows` (defaults to 100x30). Always query `list` first and pass existing dimensions when observing an existing terminal.
  - Replies with `snapshot` followed by `status`.
- `context` (attached): returns `context` object with `text` (active screen only, plain UTF-8), `title`, `pwd` (OSC 7 URI), `screen` (`primary` or `alternate`), `cursorX`, `cursorY`, `atPrompt` (OSC 133).
- `input` (attached): `{"op":"input","data":"<base64>"}`.
- `resize` (attached): `{"op":"resize","cols":120,"rows":40,"claim":true}`.
- `snapshot` / `status` / `detach` / `terminate` (attached, or unattached `terminate` with `terminalID`; managed SSH terminals reject `terminate` with `managed_disconnect_required`, use `ssh.close` instead).

### Host services v1

Request (single request per connection; server replies once and closes):

```json
{"op":"service","service":{"version":1,"id":"req-1","identity":{"serverID":"...","epoch":"..."},"method":"...","payload":{}}}
```

- Call `server.info` first without `identity` to obtain `identity` (`serverID` = persistent installation ID, `epoch` = process-local `serverID`) and `methods`.
- Limits: 64 KiB request, 2 MiB response, 30s execution deadline.
- Error `stale_identity` (phase `before_execution`): re-run `server.info` to refresh `epoch`.

#### Exact schemas for commonly used `ssh.*` and exchange methods

- `ssh.profiles.list`: `{}`
- `ssh.profiles.read`: `{"id":"<profile-uuid>"}` (field is `id`, not `profileID`)
- `ssh.connect`: `{"profileID":"<profile-uuid>","expectedRevision":<int>,"cols":120,"rows":40}` -> returns `{resource:{owner,connectionID,generation,terminalID,profileID,profileRevision},state,...}`
- `ssh.connections.read`: `{"connectionID":"<uuid>","generation":"<uuid>"}` (there is no `ssh.connections.list`; use `scripts/ibudo.py panes` or `session`)
- `ssh.connections.operation`: `{"operationID":"<uuid>"}`
- `ssh.close`: `{"connectionID":"<uuid>","generation":"<uuid>"}`
- `ssh.tools.read`: `{"connectionID":"<uuid>","generation":"<uuid>","sessionID":"<id>"}`
- `session.exchange.*` and `snippets.exchange.*` (staged binary/JSON transfer, handled by `scripts/ibudo.py session`):
  1. `begin`: `{"method":"read","size":2,"digest":"<sha256-hex>"}` (`size` must be >= 2, e.g. `b"{}"` for empty payload)
  2. `append`: `{"id":"<ex-id>","offset":0,"data":"<base64-chunk-max-32KiB>"}`
  3. `submit`: `{"id":"<ex-id>"}`
  4. `status`: `{"id":"<ex-id>"}` (poll while `state == "running"`)
  5. `page`: `{"id":"<ex-id>","offset":<byte-offset>}` (returns base64 `data` and total `size`)
  6. `release`: `{"id":"<ex-id>"}` (always release after reading)

#### Other agent-accessible methods

- Discovery & sync: `server.info`, `changes.wait` (`{"after":<rev>}`), `servers.list`
- Files & uploads: `files.{list,stat,read,search,page,watch}`, `files.upload.{destination,begin,append,commit,status,cancel,release}`, `files.paste.{begin,finish}`
- Ports & activity: `ports.scan`, `activity.{history,get,health}`
- Ordinary terminal tools: `tools.read` (`{"terminalID":"..."}`), `tools.action`
- Git & GitHub: `git.command.{start,status,input,page,cancel,ack}`, `git.lease.{acquire,renew,release}`, `git.watch`, `github.pr.{repository,list,current,detail,checks,head,createMetadata,mergeAuthority}`, `github.mutation.{begin,progress,complete,listUnfinished,recover}`
- SSH profile mutations & helpers: `ssh.profiles.{create,update,favorite,duplicate,delete,recovery,invalidDeletionToken,recover,deleteInvalid}`, `ssh.exchange.*`, `ssh.upload.*`, `ssh.git.*`

#### Owner-GUI-only methods (return `local_owner_required` to non-`Ibudo.app` callers)

- `terminal.policy.set`, `storage.status`
- `activity.append`, `activity.reclassify`
- `ssh.credentials.*`
- `servers.{add,retry,remove,setColor,rename,setEnabled}`
- `server.sock.protected`

## App local control socket (`c.sock`)

- Discovery: `IBUDO_SOCKET_PATH` if set; otherwise `/tmp/ibudo-<uid>/<namespace>/endpoint.json` (`socket_path`).
- Framing: connect, write one JSON object (max 512 KiB), call `shutdown(SHUT_WR)`, read one JSON object until EOF (max 64 KiB). 2s read and dispatch deadlines.
- Auth: same UID (`getpeereid`). `source.kind` must be `"helper"`; `source.tool` allows ASCII letters, digits, `.`, `-`, `_`.

### Addressing rules

- Concrete handles: `window:main`, `workspace:<id>`, `tab:<id>`, `slot:<id>`, `pane:<id>`.
- Selectors: `window:main`, `workspace:active`, `workspace:#<1-based>`, `tab:active`, `tab:#<1-based>`, `pane:focused`, `pane:last_terminal`, `pane:#<1-based>`.
- Mutating actions require `app_boot_id` and `context_generation` in `address`, plus concrete handles (or concrete `origin_workspace`, `origin_workspace_tab`, `origin_pane` when targeting by selector).
- `terminal.new_pane` rejects `address.pane` (`pane_not_terminal_creation_target`).
- `git.status` and `layout.get` reject `address.pane`.
- `tool.nvim.*` and `tool_context.*` require `source.tool` to be `"nvim"` or `"tmux"` with a registered `instance_id`.

### Key error codes

- `stale_request` (`context_generation_mismatch` or `app_boot_id_mismatch`): re-read `app.identify` and retry.
- `stale_target` / `target_not_found`: handle closed or invalid; re-read `layout.get`.
- `confirmation_required`: destructive action returned a single-use `confirmation_token` bound to action, target, boot ID, and generation.
- `action_unavailable` / `invalid_payload` / `unknown_action`: inspect `actions.list` for the current schema.
