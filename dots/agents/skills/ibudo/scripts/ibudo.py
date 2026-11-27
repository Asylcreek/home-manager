#!/usr/bin/env python3
"""CLI helper for Ibudo's local Unix sockets (server.sock and c.sock).

Standard library only. Supports both IbudoServer (headless terminal protocol v3
and host services v1, including managed SSH terminals and forwarded remote
servers) and Ibudo.app local control (ibudo-control v1).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
import uuid
from typing import Any

HELPER_BINARY = "/Applications/Ibudo.app/Contents/Helpers/IbudoServer.app/Contents/MacOS/IbudoServer"
WORKSPACE_TAB_ONLY_ACTIONS = {
    "terminal.new_pane",
}
EXCHANGE_CHUNK_BYTES = 32 * 1024
ANSI_RE = re.compile(r"\x1b(?:\][^\x07\x1b]*(?:\x07|\x1b\\)|\[[0-?]*[ -/]*[@-~]|[@-Z\\-_])")


def clean_pty_text(raw: bytes | bytearray) -> str:
    text = ANSI_RE.sub("", bytes(raw).decode("utf-8", errors="replace"))
    return text.replace("\r\n", "\n").replace("\r", "")


class IbudoError(RuntimeError):
    def __init__(self, message: str, exit_code: int = 1, payload: Any = None):
        super().__init__(message)
        self.exit_code = exit_code
        self.payload = payload


def default_namespace(args: argparse.Namespace) -> str:
    return getattr(args, "namespace", None) or os.environ.get("IBUDO_NAMESPACE") or "Ibudo"


def default_server_dir(namespace: str) -> str:
    return os.path.expanduser(f"~/Library/Application Support/{namespace}/server")


def default_server_socket(namespace: str) -> str:
    return os.path.join(default_server_dir(namespace), "server.sock")


def resolve_lc_socket(args: argparse.Namespace) -> str:
    if getattr(args, "socket", None):
        return args.socket
    if os.environ.get("IBUDO_SOCKET_PATH"):
        return os.environ["IBUDO_SOCKET_PATH"]
    ns = default_namespace(args)
    ep_path = f"/tmp/ibudo-{os.getuid()}/{ns}/endpoint.json"
    if not os.path.exists(ep_path):
        raise IbudoError(
            f"Ibudo local control endpoint not found at {ep_path}. Is Ibudo.app running?"
        )
    with open(ep_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    sock = data.get("socket_path")
    if not sock:
        raise IbudoError(f"endpoint.json at {ep_path} has no socket_path")
    return sock


def resolve_daemon_socket(args: argparse.Namespace) -> str:
    if getattr(args, "socket", None):
        return args.socket
    local_sock = default_server_socket(default_namespace(args))
    server_name = getattr(args, "server", None)
    if not server_name or server_name.lower() == "local":
        if not os.path.exists(local_sock):
            raise IbudoError(
                f"IbudoServer socket not found at {local_sock}. Run 'ibudo.py ensure' or launch Ibudo.app."
            )
        return local_sock
    info = ts_service(local_sock, "server.info", {}, timeout=args.timeout)
    identity = info["identity"]
    listed = ts_service(local_sock, "servers.list", {}, identity=identity, timeout=args.timeout)
    needle = server_name.lower()
    matches = []
    for row in listed["result"].get("servers", []):
        fields = [
            row.get("displayName", ""),
            row.get("profileLabel", ""),
            row.get("hostname", ""),
            row.get("target", ""),
            row.get("id", ""),
            row.get("installationID", ""),
        ]
        if any(f.lower() == needle for f in fields if f):
            matches.append(row)
    if not matches:
        available = [r.get("displayName") or r.get("id") for r in listed["result"].get("servers", [])]
        raise IbudoError(f"Remote server {server_name!r} not found. Available: {available}")
    if len(matches) > 1:
        ids = [f"{r.get('displayName')} ({r.get('id')})" for r in matches]
        raise IbudoError(f"Ambiguous server {server_name!r}: {ids}")
    row = matches[0]
    if row.get("status") != "connected" or not row.get("endpoint", {}).get("socketPath"):
        reason = row.get("reason", {}).get("code", "")
        suffix = f" ({reason})" if reason else ""
        raise IbudoError(
            f"Remote server {row.get('displayName')!r} is {row.get('status')}{suffix}, not connected."
        )
    return row["endpoint"]["socketPath"]


# ---------------------------------------------------------------------------
# Daemon socket (server.sock): Terminal protocol v3 + Host services v1
# ---------------------------------------------------------------------------


class DaemonConn:
    def __init__(self, sock_path: str, timeout: float = 10.0):
        self.sock_path = sock_path
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self.buf = bytearray()

    def __enter__(self) -> "DaemonConn":
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            s.connect(self.sock_path)
        except OSError as exc:
            s.close()
            raise IbudoError(f"Failed to connect to {self.sock_path}: {exc}") from exc
        self.sock = s
        return self

    def __exit__(self, *_exc: Any) -> None:
        if self.sock is not None:
            try:
                self.sock.close()
            finally:
                self.sock = None

    def send(self, obj: dict[str, Any]) -> None:
        assert self.sock is not None
        self.sock.sendall((json.dumps(obj, separators=(",", ":")) + "\n").encode("utf-8"))

    def recv(self, timeout: float | None = None) -> dict[str, Any]:
        assert self.sock is not None
        prev = self.sock.gettimeout()
        if timeout is not None:
            self.sock.settimeout(timeout)
        try:
            while True:
                nl = self.buf.find(b"\n")
                if nl != -1:
                    line = bytes(self.buf[:nl])
                    del self.buf[: nl + 1]
                    return json.loads(line.decode("utf-8"))
                chunk = self.sock.recv(65536)
                if not chunk:
                    raise IbudoError("Connection closed unexpectedly by IbudoServer.")
                self.buf.extend(chunk)
        except socket.timeout as exc:
            raise TimeoutError("Timed out reading from IbudoServer.") from exc
        finally:
            if timeout is not None:
                self.sock.settimeout(prev)


def ts_service(
    sock_path: str,
    method: str,
    payload: dict[str, Any] | None = None,
    identity: dict[str, str] | None = None,
    timeout: float = 15.0,
) -> dict[str, Any]:
    if identity is None and method != "server.info":
        info = ts_service(sock_path, "server.info", {}, timeout=timeout)
        identity = info["identity"]
    svc: dict[str, Any] = {
        "version": 1,
        "id": str(uuid.uuid4()),
        "method": method,
        "payload": payload if payload is not None else {},
    }
    if identity is not None:
        svc["identity"] = identity
    with DaemonConn(sock_path, timeout=timeout) as conn:
        conn.send({"op": "service", "service": svc})
        reply = conn.recv()
    if reply.get("type") == "error":
        raise IbudoError(f"Daemon error: {reply.get('message')}", payload=reply)
    body = reply.get("service", {})
    if "error" in body and body["error"]:
        err = body["error"]
        raise IbudoError(
            f"{method} failed [{err.get('code')}]: {err.get('message')}",
            payload=body,
        )
    return body


def ts_exchange(
    sock_path: str,
    prefix: str,
    method: str,
    payload: dict[str, Any] | None = None,
    identity: dict[str, str] | None = None,
    timeout: float = 15.0,
) -> Any:
    """Run a staged host exchange (<prefix>.{begin,append,submit,status,page,release})."""
    if identity is None:
        identity = ts_service(sock_path, "server.info", {}, timeout=timeout)["identity"]
    body = json.dumps(payload if payload is not None else {}, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(body).hexdigest()
    beg = ts_service(
        sock_path,
        f"{prefix}.begin",
        {"method": method, "size": len(body), "digest": digest},
        identity=identity,
        timeout=timeout,
    )["result"]
    ex_id = beg["id"]
    try:
        offset = 0
        while offset < len(body):
            chunk = body[offset : offset + EXCHANGE_CHUNK_BYTES]
            ts_service(
                sock_path,
                f"{prefix}.append",
                {"id": ex_id, "offset": offset, "data": base64.b64encode(chunk).decode("ascii")},
                identity=identity,
                timeout=timeout,
            )
            offset += len(chunk)
        receipt = ts_service(
            sock_path, f"{prefix}.submit", {"id": ex_id}, identity=identity, timeout=timeout
        )["result"]
        deadline = time.monotonic() + timeout
        while receipt.get("state") == "running":
            if time.monotonic() >= deadline:
                raise IbudoError(f"{prefix} {method} timed out waiting for completion.")
            time.sleep(0.05)
            receipt = ts_service(
                sock_path, f"{prefix}.status", {"id": ex_id}, identity=identity, timeout=timeout
            )["result"]
        if receipt.get("error"):
            raise IbudoError(
                f"{prefix} {method} failed [{receipt['error']}]", payload=receipt
            )
        out = bytearray()
        out_offset = 0
        total = int(receipt.get("size", 0))
        while out_offset < total:
            pg = ts_service(
                sock_path,
                f"{prefix}.page",
                {"id": ex_id, "offset": out_offset},
                identity=identity,
                timeout=timeout,
            )["result"]
            raw_b64 = pg.get("data", "")
            if not raw_b64:
                break
            chunk = base64.b64decode(raw_b64)
            out.extend(chunk)
            out_offset += len(chunk)
    finally:
        try:
            ts_service(sock_path, f"{prefix}.release", {"id": ex_id}, identity=identity, timeout=5.0)
        except Exception:
            pass
    text = out.decode("utf-8").strip()
    if not text:
        return {}
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) == 1:
        return json.loads(lines[0])
    return [json.loads(ln) for ln in lines]


def ts_session_read(
    sock_path: str, include_lineage: bool = False, timeout: float = 15.0
) -> dict[str, Any]:
    req = {"includeLineage": True} if include_lineage else {}
    return ts_exchange(sock_path, "session.exchange", "read", req, timeout=timeout)


def ts_list(conn: DaemonConn) -> list[dict[str, Any]]:
    conn.send({"op": "list"})
    ev = conn.recv()
    if ev.get("type") == "error":
        raise IbudoError(f"list failed: {ev.get('message')}", payload=ev)
    return ev.get("terminals", [])


def build_pane_inventory(sock_path: str, timeout: float = 15.0) -> list[dict[str, Any]]:
    """Join saved session panes with live IbudoServer terminals (works headless)."""
    with DaemonConn(sock_path, timeout=timeout) as conn:
        live_terms = ts_list(conn)
    live_by_id = {t["terminalID"]: t for t in live_terms}
    seen_terms: set[str] = set()

    session = ts_session_read(sock_path, timeout=timeout)
    snap = session.get("snapshot", {})

    ws_names: dict[str, str] = {}
    for ws in snap.get("workspaces", []):
        try:
            wp = json.loads(ws.get("payload", "{}"))
        except json.JSONDecodeError:
            wp = {}
        ws_names[ws["id"]] = wp.get("name") or ws["id"]

    tabs_meta: dict[str, dict[str, Any]] = {}
    for tab in snap.get("workspaceTabs", []):
        try:
            tp = json.loads(tab.get("payload", "{}"))
        except json.JSONDecodeError:
            tp = {}
        tabs_meta[tab["id"]] = {
            "workspaceID": tab.get("workspaceID"),
            "workspaceName": ws_names.get(tab.get("workspaceID", ""), tab.get("workspaceID", "")),
            "title": tp.get("customTitle") or tp.get("generatedTitle") or tab["id"],
        }

    records: list[dict[str, Any]] = []
    for pt in snap.get("paneTabs", []):
        pane_id = pt["id"]
        kind = pt.get("kind", "")
        tab_id = pt.get("workspaceTabID", "")
        tmeta = tabs_meta.get(tab_id, {})
        try:
            pp = json.loads(pt.get("payload", "{}"))
        except json.JSONDecodeError:
            pp = {}

        ssh_ctx = pp.get("sshTerminalContext") or {}
        sr = ssh_ctx.get("serverResource") or {}
        conn_id = sr.get("connectionID")
        generation = sr.get("generation")
        ssh_label = ssh_ctx.get("resolvedDisplayLabel")
        launch_snap = (ssh_ctx.get("launchIdentity") or {}).get("snapshot") or {}

        if kind == "sshTerminal":
            term_id = sr.get("terminalID") or (f"ssh-{conn_id}" if conn_id else None)
        elif kind == "terminal":
            term_id = pane_id
        else:
            term_id = None

        live = live_by_id.get(term_id) if term_id else None
        if term_id and live:
            seen_terms.add(term_id)

        label = (
            pp.get("customTitle")
            or ssh_label
            or pp.get("generatedTitle")
            or pp.get("lastProgramTitle")
            or pane_id
        )
        rec: dict[str, Any] = {
            "paneID": pane_id,
            "paneHandle": f"pane:{pane_id}",
            "kind": kind,
            "workspaceID": tmeta.get("workspaceID"),
            "workspace": tmeta.get("workspaceName"),
            "tabID": tab_id,
            "tab": tmeta.get("title"),
            "label": label,
            "generatedTitle": pp.get("generatedTitle"),
            "title": pp.get("lastProgramTitle") or label,
            "terminalID": term_id,
            "live": live is not None,
        }
        if kind == "sshTerminal":
            rec["ssh"] = {
                "profile": ssh_label or launch_snap.get("displayName"),
                "address": launch_snap.get("address"),
                "connectionID": conn_id,
                "generation": generation,
            }
        if live is not None:
            rec["pid"] = live.get("pid")
            rec["cols"] = live.get("cols")
            rec["rows"] = live.get("rows")
            rec["busy"] = live.get("busy", False)
            rec["exited"] = live.get("exited", False)
            if "exitCode" in live:
                rec["exitCode"] = live["exitCode"]
        records.append(rec)

    # Append any headless/orphan live terminals not bound to a saved session pane.
    for tid, live in live_by_id.items():
        if tid in seen_terms:
            continue
        records.append(
            {
                "paneID": None,
                "paneHandle": None,
                "kind": "sshTerminal" if tid.startswith("ssh-") else "headlessTerminal",
                "workspaceID": None,
                "workspace": None,
                "tabID": None,
                "tab": None,
                "label": tid,
                "generatedTitle": None,
                "title": tid,
                "terminalID": tid,
                "live": True,
                "pid": live.get("pid"),
                "cols": live.get("cols"),
                "rows": live.get("rows"),
                "busy": live.get("busy", False),
                "exited": live.get("exited", False),
                **({"exitCode": live["exitCode"]} if "exitCode" in live else {}),
            }
        )
    return records


def resolve_terminal_target(
    sock_path: str,
    raw_id: str,
    live_by_id: dict[str, dict[str, Any]],
    connection_id: str | None = None,
    generation: str | None = None,
    timeout: float = 15.0,
) -> tuple[str, dict[str, Any], dict[str, str] | None]:
    """Resolve a terminalID, pane:<uuid>, pane UUID, or SSH connectionID to (terminalID, info, managed)."""
    target = raw_id[5:] if raw_id.startswith("pane:") else raw_id

    if connection_id and generation:
        tid = target if target in live_by_id else f"ssh-{connection_id}"
        if tid not in live_by_id:
            raise IbudoError(f"Terminal {tid!r} not found in live terminals.")
        return tid, live_by_id[tid], {"connectionID": connection_id, "generation": generation}

    # Fast path for ordinary local terminals.
    if target in live_by_id and not target.startswith("ssh-"):
        return target, live_by_id[target], None

    # Managed SSH terminal or pane UUID -> consult session snapshot.
    try:
        panes = build_pane_inventory(sock_path, timeout=timeout)
    except IbudoError:
        panes = []

    for rec in panes:
        ssh = rec.get("ssh") or {}
        candidates = {
            rec.get("paneID"),
            rec.get("terminalID"),
            ssh.get("connectionID"),
        }
        if target in candidates:
            tid = rec.get("terminalID")
            if not tid or tid not in live_by_id:
                raise IbudoError(
                    f"Pane {raw_id!r} ({rec.get('kind')}) has no live terminal (terminalID={tid!r})."
                )
            managed = None
            if tid.startswith("ssh-"):
                cid = connection_id or ssh.get("connectionID")
                gen = generation or ssh.get("generation")
                if not cid or not gen:
                    raise IbudoError(
                        f"Managed SSH terminal {tid!r} requires --connection-id and --generation "
                        "(not found in saved session snapshot)."
                    )
                managed = {"connectionID": cid, "generation": gen}
            return tid, live_by_id[tid], managed

    if target in live_by_id and target.startswith("ssh-"):
        raise IbudoError(
            f"Terminal {target!r} is a managed SSH session not found in the saved session snapshot. "
            "Pass --connection-id and --generation explicitly."
        )
    raise IbudoError(
        f"Terminal or pane {raw_id!r} not found. Run 'ibudo.py panes' or 'ibudo.py terminals' to list live targets."
    )


def ts_attach_existing(
    conn: DaemonConn,
    sock_path: str,
    raw_id: str,
    allow_exited: bool = False,
    connection_id: str | None = None,
    generation: str | None = None,
    timeout: float = 15.0,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    live_by_id = {t["terminalID"]: t for t in ts_list(conn)}
    tid, info, managed = resolve_terminal_target(
        sock_path,
        raw_id,
        live_by_id,
        connection_id=connection_id,
        generation=generation,
        timeout=timeout,
    )
    if info.get("exited") and not allow_exited:
        raise IbudoError(
            f"Terminal {tid!r} has already exited (exitCode={info.get('exitCode')})."
        )
    req: dict[str, Any] = {
        "op": "attach",
        "backend": "ghostty",
        "terminalID": tid,
        "cols": info["cols"],
        "rows": info["rows"],
    }
    if managed is not None:
        req["managed"] = managed
    conn.send(req)
    snap, status = _drain_attach(conn)
    return tid, snap, status


def _drain_attach(conn: DaemonConn) -> tuple[dict[str, Any], dict[str, Any]]:
    snap: dict[str, Any] | None = None
    status: dict[str, Any] | None = None
    while snap is None or status is None:
        ev = conn.recv()
        etype = ev.get("type")
        if etype == "error":
            raise IbudoError(f"attach failed: {ev.get('message')}", payload=ev)
        if etype == "lost":
            raise IbudoError(f"Terminal {ev.get('terminalID')!r} was lost on server restart.", payload=ev)
        if etype == "exited":
            raise IbudoError(
                f"Terminal {ev.get('terminalID')!r} exited (exitCode={ev.get('exitCode')}).",
                payload=ev,
            )
        if etype == "snapshot":
            snap = ev
        elif etype == "status":
            status = ev
    return snap, status


def ts_request_context(
    conn: DaemonConn, capture: bytearray | None = None
) -> dict[str, Any]:
    conn.send({"op": "context"})
    while True:
        ev = conn.recv()
        etype = ev.get("type")
        if etype == "output" and capture is not None and ev.get("data"):
            capture.extend(base64.b64decode(ev["data"]))
            continue
        if etype == "context":
            return ev
        if etype == "error":
            raise IbudoError(f"context failed: {ev.get('message')}", payload=ev)


# ---------------------------------------------------------------------------
# App local control socket (c.sock): ibudo-control v1
# ---------------------------------------------------------------------------


def lc_call(
    sock_path: str,
    intent: dict[str, Any],
    address: dict[str, Any] | None = None,
    tool: str = "ibudo-cli",
    timeout: float = 5.0,
) -> dict[str, Any]:
    req: dict[str, Any] = {
        "protocol": "ibudo-control",
        "schema_version": 1,
        "request_id": str(uuid.uuid4()),
        "source": {"kind": "helper", "tool": tool, "version": "1"},
        "intent": intent,
    }
    if address:
        req["address"] = address
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect(sock_path)
        except OSError as exc:
            raise IbudoError(f"Failed to connect to local control socket {sock_path}: {exc}") from exc
        s.sendall(json.dumps(req, separators=(",", ":")).encode("utf-8"))
        s.shutdown(socket.SHUT_WR)
        chunks = []
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    if not chunks:
        raise IbudoError("Empty response from local control socket.")
    resp = json.loads(b"".join(chunks).decode("utf-8"))
    if not resp.get("ok"):
        err = resp.get("error", {})
        parts = [err.get("code", "error")]
        if err.get("diagnostic_code"):
            parts.append(err["diagnostic_code"])
        msg = err.get("detail") or err.get("message") or "Local control request failed."
        raise IbudoError(f"Local control failed [{':'.join(parts)}]: {msg}", payload=resp)
    return resp


def normalize_handle(value: str, prefix: str) -> str:
    if ":" in value:
        return value
    return f"{prefix}:{value}"


def is_selector(value: str) -> bool:
    return value in {
        "window:main",
        "workspace:active",
        "tab:active",
        "pane:focused",
        "pane:last_terminal",
    } or value.startswith(("workspace:#", "tab:#", "pane:#"))


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def emit(args: argparse.Namespace, data: Any, human_fn=None) -> None:
    if args.json or human_fn is None:
        print(json.dumps(data, indent=2))
    else:
        human_fn(data)


def parse_json_arg(raw: str | None, label: str = "payload") -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise IbudoError(f"Invalid JSON for {label}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise IbudoError(f"Expected JSON object for {label}.")
    return parsed


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def cmd_ensure(args: argparse.Namespace) -> None:
    ns = default_namespace(args)
    state_dir = default_server_dir(ns)
    sock = getattr(args, "socket", None) or os.path.join(state_dir, "server.sock")
    helper = args.helper or HELPER_BINARY
    if not os.path.exists(helper):
        raise IbudoError(f"IbudoServer helper not found at {helper}")
    proc = subprocess.run(
        [helper, "--ensure", "--socket", sock, "--state-dir", state_dir, "--mac-storage"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if proc.returncode != 0:
        raise IbudoError(f"IbudoServer --ensure failed (exit {proc.returncode}): {proc.stderr.strip()}")
    lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    out = {
        "serverID": lines[0] if lines else "",
        "outdated": len(lines) > 1 and lines[1] == "outdated",
        "socket": sock,
        "stateDir": state_dir,
    }
    emit(
        args,
        out,
        lambda d: print(
            f"IbudoServer ready: serverID={d['serverID']} socket={d['socket']}"
            + (" (outdated)" if d["outdated"] else "")
        ),
    )


def cmd_hello(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    with DaemonConn(sock, timeout=args.timeout) as conn:
        conn.send({"op": "hello"})
        ev = conn.recv()
    emit(
        args,
        ev,
        lambda d: print(
            f"protocol={d.get('protocolVersion')} pid={d.get('serverPID')} "
            f"serverID={d.get('serverID')} replaced={d.get('replaced', False)}"
        ),
    )


def cmd_servers(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    reply = ts_service(sock, "servers.list", {}, timeout=args.timeout)
    result = reply["result"]

    def show(res: dict[str, Any]) -> None:
        loc = res.get("local", {})
        print(
            f"local  {loc.get('hostname', '?')} ({loc.get('deviceKind', '?')})  "
            f"protocol={loc.get('protocolVersion', '?')}  socket={sock}"
        )
        for row in res.get("servers", []):
            ep = row.get("endpoint", {}).get("socketPath", "")
            reason = row.get("reason", {}).get("code", "")
            detail = ep or reason or ("disabled" if row.get("disabled") else "")
            print(
                f"{row.get('status', '?'):10s}  {row.get('displayName', '?'):16s}  "
                f"{row.get('target', ''):20s}  {detail}"
            )

    emit(args, result, show)


def cmd_session(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    data = ts_session_read(sock, include_lineage=args.lineage, timeout=args.timeout)

    def show(d: dict[str, Any]) -> None:
        snap = d.get("snapshot", {})
        print(
            f"sessionRevision={d.get('sessionRevision')}  "
            f"windows={len(snap.get('windows', []))}  "
            f"workspaces={len(snap.get('workspaces', []))}  "
            f"tabs={len(snap.get('workspaceTabs', []))}  "
            f"panes={len(snap.get('paneTabs', []))}"
        )
        if d.get("lineage"):
            print(f"lineage={d['lineage']}")

    emit(args, data, show)


def cmd_panes(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    records = build_pane_inventory(sock, timeout=args.timeout)
    if args.live_only:
        records = [r for r in records if r.get("live")]
    if args.filter:
        needle = args.filter.lower()

        def matches(r: dict[str, Any]) -> bool:
            ssh = r.get("ssh") or {}
            haystack = " ".join(
                str(v)
                for v in (
                    r.get("paneID"),
                    r.get("terminalID"),
                    r.get("kind"),
                    r.get("workspace"),
                    r.get("tab"),
                    r.get("label"),
                    r.get("generatedTitle"),
                    r.get("title"),
                    ssh.get("profile"),
                    ssh.get("address"),
                )
                if v
            ).lower()
            return needle in haystack

        records = [r for r in records if matches(r)]

    def show(rows: list[dict[str, Any]]) -> None:
        if not rows:
            print("(no matching panes)")
            return
        for r in rows:
            pid_col = r["paneHandle"] or "(headless)"
            kind = r["kind"]
            loc = f"{r['workspace']}/{r['tab']}" if r.get("workspace") else "-"
            label = r.get("label") or ""
            title = r.get("title") or ""
            title_part = f"{label} ({title})" if title and title != label else label
            if r.get("live"):
                state = (
                    f"exited({r.get('exitCode')})"
                    if r.get("exited")
                    else ("busy" if r.get("busy") else "idle")
                )
                term_part = f"term={r['terminalID']} {r.get('cols', 0)}x{r.get('rows', 0)} {state}"
            elif r.get("terminalID"):
                term_part = f"term={r['terminalID']} (not running)"
            else:
                term_part = "(non-terminal)"
            print(f"{pid_col}  [{kind}]  {loc}  {title_part}  |  {term_part}")

    emit(args, records, show)


def cmd_terminals(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    with DaemonConn(sock, timeout=args.timeout) as conn:
        terms = ts_list(conn)

    def show(rows: list[dict[str, Any]]) -> None:
        if not rows:
            print("(no live terminals)")
            return
        for t in rows:
            state = f"exited({t.get('exitCode')})" if t.get("exited") else ("busy" if t.get("busy") else "idle")
            print(
                f"{t['terminalID']}  pid={t.get('pid', 0):<7d}  "
                f"{t.get('cols', 0)}x{t.get('rows', 0):<4d}  {state}"
            )

    emit(args, terms, show)


def cmd_read(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    with DaemonConn(sock, timeout=args.timeout) as conn:
        tid, snap, status = ts_attach_existing(
            conn,
            sock,
            args.terminal_id,
            allow_exited=False,
            connection_id=args.connection_id,
            generation=args.generation,
            timeout=args.timeout,
        )
        if args.snapshot:
            raw_bytes = base64.b64decode(snap.get("data", ""))
            conn.send({"op": "detach"})
            out = {
                "terminalID": tid,
                "cols": status.get("cols"),
                "rows": status.get("rows"),
                "busy": status.get("busy"),
                "text": raw_bytes.decode("utf-8", errors="replace"),
            }
            emit(args, out, lambda d: print(d["text"]))
            return
        ev = ts_request_context(conn)
        conn.send({"op": "detach"})

    ctx = ev.get("context", {})
    out = {
        "terminalID": tid,
        "pid": ev.get("pid"),
        "cols": ev.get("cols"),
        "rows": ev.get("rows"),
        "busy": ev.get("busy"),
        "exited": ev.get("exited"),
        "context": ctx,
    }

    def show(d: dict[str, Any]) -> None:
        c = d["context"]
        print(
            f"# {d['terminalID']} ({d['cols']}x{d['rows']}) "
            f"screen={c.get('screen')} atPrompt={c.get('atPrompt')} busy={d['busy']}"
        )
        if c.get("pwd"):
            print(f"# pwd: {c['pwd']}")
        if c.get("title"):
            print(f"# title: {c['title']}")
        print(c.get("text", ""), end="" if c.get("text", "").endswith("\n") else "\n")

    emit(args, out, show)


def _drain_output_until(
    conn: DaemonConn,
    wait_seconds: float,
    wait_prompt: bool,
    had_osc133: bool,
    quiet_seconds: float,
) -> tuple[bytearray, dict[str, Any], bool]:
    """Drain PTY output events for a fixed duration or until the shell returns to prompt."""
    captured = bytearray()
    start = time.monotonic()
    deadline = start + max(wait_seconds, 0.0)
    last_output_at = start
    saw_output = False
    timed_out = False

    if not wait_prompt:
        while time.monotonic() < deadline:
            remaining = max(0.02, deadline - time.monotonic())
            try:
                ev = conn.recv(timeout=min(0.2, remaining))
            except TimeoutError:
                continue
            if ev.get("type") == "output" and ev.get("data"):
                captured.extend(base64.b64decode(ev["data"]))
        ctx_ev = ts_request_context(conn, capture=captured)
        return captured, ctx_ev, False

    # Wait-prompt mode: wait until OSC 133 atPrompt returns (or quiet idle if shell has no OSC 133).
    saw_busy_or_left_prompt = False
    while time.monotonic() < deadline:
        remaining = max(0.05, deadline - time.monotonic())
        try:
            ev = conn.recv(timeout=min(0.2, remaining))
            if ev.get("type") == "output" and ev.get("data"):
                captured.extend(base64.b64decode(ev["data"]))
                last_output_at = time.monotonic()
                saw_output = True
            elif ev.get("type") == "exited":
                break
        except TimeoutError:
            pass

        now = time.monotonic()
        if now - start < 0.2:
            continue
        ctx_ev = ts_request_context(conn, capture=captured)
        ctx = ctx_ev.get("context", {})
        busy = bool(ctx_ev.get("busy"))
        at_prompt = bool(ctx.get("atPrompt"))
        if busy or not at_prompt:
            saw_busy_or_left_prompt = True
        if had_osc133:
            if not busy and at_prompt and (saw_busy_or_left_prompt or (saw_output and now - last_output_at >= 0.25)):
                return captured, ctx_ev, False
        else:
            if not busy and saw_output and (now - last_output_at >= quiet_seconds):
                return captured, ctx_ev, False
    else:
        timed_out = True

    ctx_ev = ts_request_context(conn, capture=captured)
    return captured, ctx_ev, timed_out


def cmd_send(args: argparse.Namespace) -> None:
    if args.stdin:
        text = sys.stdin.read()
    elif args.text is not None:
        text = args.text
    else:
        raise IbudoError("Provide text argument or --stdin.")
    if args.enter:
        text += "\r"

    sock = resolve_daemon_socket(args)
    with DaemonConn(sock, timeout=args.timeout) as conn:
        tid, _, status = ts_attach_existing(
            conn,
            sock,
            args.terminal_id,
            connection_id=args.connection_id,
            generation=args.generation,
            timeout=args.timeout,
        )
        before_ctx = None
        if args.if_at_prompt or args.if_idle or args.wait_prompt:
            before_ev = ts_request_context(conn)
            before_ctx = before_ev.get("context", {})
            if args.if_at_prompt and (before_ev.get("busy") or not before_ctx.get("atPrompt")):
                conn.send({"op": "detach"})
                raise IbudoError(
                    f"Refusing to send input: busy={before_ev.get('busy')}, "
                    f"atPrompt={before_ctx.get('atPrompt')}",
                    exit_code=3,
                )
            if args.if_idle and (before_ev.get("busy") or before_ctx.get("screen") != "primary"):
                conn.send({"op": "detach"})
                raise IbudoError(
                    f"Refusing to send input: busy={before_ev.get('busy')}, "
                    f"screen={before_ctx.get('screen')}",
                    exit_code=3,
                )

        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        conn.send({"op": "input", "data": encoded})
        out: dict[str, Any] = {
            "terminalID": tid,
            "bytesSent": len(text.encode("utf-8")),
            "cols": status.get("cols"),
            "rows": status.get("rows"),
        }
        wait_secs = args.wait if args.wait > 0 else (args.timeout if args.wait_prompt else 0.0)
        if args.wait_prompt or wait_secs > 0:
            captured, ctx_ev, timed_out = _drain_output_until(
                conn,
                wait_seconds=wait_secs,
                wait_prompt=args.wait_prompt,
                had_osc133=bool(before_ctx and before_ctx.get("atPrompt")),
                quiet_seconds=args.quiet,
            )
            out["context"] = ctx_ev.get("context", {})
            out["busy"] = ctx_ev.get("busy")
            out["timedOut"] = timed_out
            if args.capture:
                out["output"] = clean_pty_text(captured)
        conn.send({"op": "detach"})

    def show(d: dict[str, Any]) -> None:
        print(f"Sent {d['bytesSent']} bytes to {d['terminalID']}")
        if d.get("timedOut"):
            print(f"[timed out waiting for prompt]", file=sys.stderr)
        if "output" in d:
            print(d["output"])
        elif "context" in d:
            print(d["context"].get("text", ""))

    emit(args, out, show)


def cmd_spawn(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    tid = args.id or f"agent-{uuid.uuid4()}"
    attach: dict[str, Any] = {
        "op": "attach",
        "backend": "ghostty",
        "terminalID": tid,
        "cols": args.cols,
        "rows": args.rows,
        "hostDefaults": True,
    }
    if args.cwd:
        attach["cwd"] = os.path.abspath(args.cwd) if not getattr(args, "server", None) else args.cwd
    if args.recreate:
        attach["recreate"] = True
    with DaemonConn(sock, timeout=args.timeout) as conn:
        conn.send(attach)
        _, status = _drain_attach(conn)
        conn.send({"op": "detach"})
    out = {
        "terminalID": status.get("terminalID", tid),
        "pid": status.get("pid"),
        "cols": status.get("cols"),
        "rows": status.get("rows"),
    }
    emit(args, out, lambda d: print(f"{d['terminalID']}  pid={d['pid']}  {d['cols']}x{d['rows']}"))


def cmd_terminate(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    tid = args.terminal_id[5:] if args.terminal_id.startswith("pane:") else args.terminal_id
    with DaemonConn(sock, timeout=args.timeout) as conn:
        conn.send({"op": "terminate", "terminalID": tid})
        ev = conn.recv()
    if ev.get("type") == "error":
        raise IbudoError(f"terminate failed: {ev.get('message')}", payload=ev)
    emit(args, ev, lambda d: print(f"{d.get('type')}: {d.get('terminalID', tid)}"))


def cmd_run(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    tid = args.id or f"agent-{uuid.uuid4()}"
    nonce = uuid.uuid4().hex[:12]
    start_marker = f"__IBUDO_START_{nonce}__"
    end_prefix = f"__IBUDO_DONE_{nonce}="
    attach: dict[str, Any] = {
        "op": "attach",
        "backend": "ghostty",
        "terminalID": tid,
        "cols": args.cols,
        "rows": args.rows,
        "hostDefaults": True,
    }
    if args.cwd:
        attach["cwd"] = os.path.abspath(args.cwd) if not getattr(args, "server", None) else args.cwd

    captured = bytearray()
    exit_code: int | None = None
    timed_out = False

    with DaemonConn(sock, timeout=args.timeout) as conn:
        try:
            conn.send(attach)
            _drain_attach(conn)
            prompt_deadline = time.monotonic() + min(3.0, args.timeout)
            while time.monotonic() < prompt_deadline:
                ctx_ev = ts_request_context(conn)
                if ctx_ev.get("context", {}).get("atPrompt"):
                    break
                time.sleep(0.1)

            wrapped = (
                f"printf '\\n%s\\n' '__IBUDO_START_'\"{nonce}\"__; "
                f"({args.command}); "
                f"__ec=$?; printf '\\n%s%d__\\n' '__IBUDO_DONE_'\"{nonce}=\" \"$__ec\"\r"
            )
            conn.send({"op": "input", "data": base64.b64encode(wrapped.encode("utf-8")).decode("ascii")})

            end_re = re.compile(re.escape(end_prefix) + r"(-?\d+)__")
            deadline = time.monotonic() + args.timeout
            while time.monotonic() < deadline:
                remaining = max(0.05, deadline - time.monotonic())
                try:
                    ev = conn.recv(timeout=min(0.5, remaining))
                except TimeoutError:
                    continue
                etype = ev.get("type")
                if etype == "output" and ev.get("data"):
                    captured.extend(base64.b64decode(ev["data"]))
                    decoded = ANSI_RE.sub("", captured.decode("utf-8", errors="replace"))
                    m = end_re.search(decoded)
                    if m:
                        exit_code = int(m.group(1))
                        break
                elif etype == "exited":
                    exit_code = ev.get("exitCode")
                    break
            else:
                timed_out = True

            ctx_ev = ts_request_context(conn)
            ctx = ctx_ev.get("context", {})
        finally:
            try:
                conn.send({"op": "detach" if args.keep else "terminate"})
            except Exception:
                pass

    clean = clean_pty_text(captured)
    body = clean
    if start_marker in body:
        body = body.split(start_marker, 1)[1]
    if end_prefix in body:
        body = body.split(end_prefix, 1)[0]
    body = body.strip("\n")

    out = {
        "terminalID": tid,
        "kept": bool(args.keep),
        "exitCode": exit_code,
        "timedOut": timed_out,
        "output": body,
        "screen": ctx.get("text", ""),
    }

    def show(d: dict[str, Any]) -> None:
        if d["output"]:
            print(d["output"])
        if d["timedOut"]:
            print(f"[timed out after {args.timeout}s]", file=sys.stderr)
        if d["kept"]:
            print(f"[kept terminal: {d['terminalID']}]", file=sys.stderr)

    emit(args, out, show)
    if timed_out:
        sys.exit(124)
    if exit_code not in (None, 0):
        sys.exit(exit_code if exit_code > 0 else 1)


def cmd_service(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    payload = parse_json_arg(args.payload, "payload")
    reply = ts_service(sock, args.method, payload, timeout=args.timeout)
    emit(args, reply if args.raw else reply.get("result"))


def cmd_ports(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    reply = ts_service(sock, "ports.scan", {}, timeout=args.timeout)
    res = reply["result"]
    listeners_raw = base64.b64decode(res.get("listeners", {}).get("stdout", "")).decode("utf-8", errors="replace")
    procs_raw = base64.b64decode(res.get("processes", {}).get("stdout", "")).decode("utf-8", errors="replace")
    proc_map: dict[str, str] = {}
    for line in procs_raw.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) >= 2:
            proc_map[parts[0]] = parts[2] if len(parts) == 3 else parts[1]
    rows = []
    cur_pid = ""
    cur_cmd = ""
    for line in listeners_raw.splitlines():
        if not line:
            continue
        tag, val = line[0], line[1:]
        if tag == "p":
            cur_pid = val
        elif tag == "c":
            cur_cmd = val
        elif tag == "n":
            rows.append({"pid": cur_pid, "comm": cur_cmd, "address": val, "command": proc_map.get(cur_pid, "")})

    def show(items: list[dict[str, str]]) -> None:
        if not items:
            print("(no listening TCP ports)")
            return
        for r in items:
            print(f"pid={r['pid']:<7s}  {r['address']:26s}  {r['comm']:16s}  {r['command']}")

    emit(args, rows, show)


def cmd_activity(args: argparse.Namespace) -> None:
    sock = resolve_daemon_socket(args)
    flt: dict[str, str] = {}
    for key in ("category", "severity", "status", "action_id", "pane_id"):
        val = getattr(args, key, None)
        if val:
            api_key = {"action_id": "actionID", "pane_id": "paneID"}.get(key, key)
            flt[api_key] = val
    reply = ts_service(
        sock,
        "activity.history",
        {"limit": args.limit, "offset": args.offset, "filter": flt},
        timeout=args.timeout,
    )
    res = reply["result"]

    def show(d: dict[str, Any]) -> None:
        for ev in d.get("events", []):
            print(
                f"{ev.get('occurredAt', '')}  [{ev.get('severity', '')}/{ev.get('status', '')}]  "
                f"{ev.get('eventType', '')}: {ev.get('summary', '')}"
            )

    emit(args, res, show)


# ---------------------------------------------------------------------------
# Local control (c.sock) subcommands
# ---------------------------------------------------------------------------


def cmd_identify(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    resp = lc_call(sock, {"kind": "app.identify"}, timeout=args.timeout)
    data = resp["data"]

    def show(d: dict[str, Any]) -> None:
        print(
            f"pid={d.get('pid')}  bundle={d.get('bundle_id')}  "
            f"boot={d.get('app_boot_id')}  gen={d.get('context_generation')}"
        )
        ws = d.get("selected_workspace") or {}
        tab = d.get("selected_tab") or {}
        pane = d.get("delivery_target_pane") or d.get("selected_pane") or {}
        print(f"workspace: {ws.get('handle')} ({ws.get('name')})")
        print(f"tab:       {tab.get('handle')} ({tab.get('title')})")
        print(f"pane:      {pane.get('handle')} [{pane.get('kind')}] ({pane.get('title')})")

    emit(args, resp if args.json else data, show)


def cmd_layout(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    addr: dict[str, Any] = {}
    if args.workspace:
        addr["workspace"] = normalize_handle(args.workspace, "workspace")
    if args.tab:
        addr["workspace_tab"] = normalize_handle(args.tab, "tab")
    resp = lc_call(sock, {"kind": "layout.get"}, address=addr or None, timeout=args.timeout)
    data = resp["data"]

    def show(d: dict[str, Any]) -> None:
        print(f"context_generation={d.get('context_generation')}")
        if d.get("workspaces"):
            print("Machines & workspaces:")
            for w in d["workspaces"]:
                print(f"  [{w.get('machine_name')}] {w.get('name')} (workspace:{w.get('workspace_id')})")
        for win in d.get("windows", []):
            print(f"\n{win.get('handle')} (focused={win.get('focused_pane')}):")
            for ws in win.get("workspaces", []):
                mark = "*" if ws.get("selected") else " "
                print(f" {mark} {ws['handle']}  {ws.get('name')}")
                for tab in ws.get("tabs", []):
                    tmark = "*" if tab.get("selected") else " "
                    print(f"   {tmark} {tab['handle']}  {tab.get('title')}")
                    for slot in tab.get("slots", []):
                        for pane in slot.get("panes", []):
                            pmark = "*" if pane["handle"] == tab.get("selected_pane") else " "
                            print(
                                f"     {pmark} {pane['handle']}  [{pane.get('kind')}]  {pane.get('title')}"
                            )

    emit(args, resp if args.json else data, show)


def cmd_context(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    addr: dict[str, Any] = {}
    if args.workspace:
        addr["workspace"] = normalize_handle(args.workspace, "workspace")
    if args.tab:
        addr["workspace_tab"] = normalize_handle(args.tab, "tab")
    if args.pane:
        addr["pane"] = normalize_handle(args.pane, "pane")
    resp = lc_call(sock, {"kind": "context.current"}, address=addr or None, timeout=args.timeout)
    emit(args, resp if args.json else resp["data"])


def cmd_actions(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    resp = lc_call(sock, {"kind": "actions.list"}, timeout=args.timeout)
    actions = resp["data"].get("actions", [])
    if args.filter:
        needle = args.filter.lower()
        actions = [a for a in actions if needle in a["id"].lower() or needle in a.get("title", "").lower()]

    def show(rows: list[dict[str, Any]]) -> None:
        for a in rows:
            req = [
                f"{f['field']}:{f['type']}"
                for f in a.get("payload_schema", {}).get("fields", [])
                if f.get("required")
            ]
            confirm = " [confirm]" if a.get("requires_confirmation") else ""
            req_str = f"  req=({', '.join(req)})" if req else ""
            print(f"{a['id']}{confirm}{req_str}")

    emit(args, actions, show)


def cmd_ssh_profiles(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    resp = lc_call(sock, {"kind": "ssh.profiles.list"}, timeout=args.timeout)
    profiles = resp["data"].get("profiles", [])

    def show(rows: list[dict[str, Any]]) -> None:
        for p in rows:
            host = (p.get("host_summary") or {}).get("host", "?")
            port = (p.get("host_summary") or {}).get("port")
            host_str = f"{host}:{port}" if port else host
            live = len(p.get("live_panes") or [])
            live_str = f"  live={live}" if live else ""
            print(f"{p.get('display_name') or '?':22s}  {host_str:28s}  id={p.get('profile_id')}{live_str}")

    emit(args, resp["data"] if args.json else profiles, show)


def cmd_git_status(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    tab = normalize_handle(args.tab, "tab") if args.tab else "tab:active"
    resp = lc_call(sock, {"kind": "git.status"}, address={"workspace_tab": tab}, timeout=args.timeout)
    emit(args, resp if args.json else resp["data"])


def cmd_search(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    tab = normalize_handle(args.tab, "tab") if args.tab else "tab:active"
    resp = lc_call(
        sock,
        {"kind": "search.query", "payload": {"query": args.query, "limit": args.limit}},
        address={"workspace_tab": tab},
        timeout=args.timeout,
    )
    results = resp["data"].get("results", [])

    def show(rows: list[dict[str, Any]]) -> None:
        for r in rows:
            req = r.get("request")
            replay = req.get("action_id") if isinstance(req, dict) else "not-replayable"
            print(f"[{r.get('type')}] {r.get('title')}  ({r.get('subtitle') or ''})  -> {replay}")

    emit(args, resp["data"] if args.json else results, show)


def cmd_settings_get(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    resp = lc_call(
        sock,
        {"kind": "settings.get", "payload": {"setting": args.setting}},
        timeout=args.timeout,
    )
    emit(args, resp if args.json else resp["data"])


def cmd_action(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    payload = parse_json_arg(args.payload, "payload")

    ident = lc_call(sock, {"kind": "app.identify"}, timeout=args.timeout)
    idata = ident["data"]
    itarget = ident.get("target") or {}

    origin_ws = itarget.get("workspace") or (idata.get("selected_workspace") or {}).get("handle")
    origin_tab = itarget.get("workspace_tab") or (idata.get("selected_tab") or {}).get("handle")
    origin_pane = (
        itarget.get("pane")
        or (idata.get("delivery_target_pane") or {}).get("handle")
        or (idata.get("selected_pane") or {}).get("handle")
    )

    ws = normalize_handle(args.workspace, "workspace") if args.workspace else origin_ws
    tab = normalize_handle(args.tab, "tab") if args.tab else origin_tab
    pane = normalize_handle(args.pane, "pane") if args.pane else origin_pane

    address: dict[str, Any] = {
        "app_boot_id": idata["app_boot_id"],
        "context_generation": idata["context_generation"],
    }
    if ws:
        address["workspace"] = ws
        if is_selector(ws) and origin_ws:
            address["origin_workspace"] = origin_ws
    if tab:
        address["workspace_tab"] = tab
        if is_selector(tab) and origin_tab:
            address["origin_workspace_tab"] = origin_tab
    if pane and args.action_id not in WORKSPACE_TAB_ONLY_ACTIONS:
        address["pane"] = pane
        if is_selector(pane) and origin_pane:
            address["origin_pane"] = origin_pane

    intent: dict[str, Any] = {
        "kind": "action.availability" if args.availability else "action.run",
        "action_id": args.action_id,
        "payload": payload,
    }
    if args.confirm:
        intent["confirmation_token"] = args.confirm
    if args.background:
        intent["background"] = True

    resp = lc_call(sock, intent, address=address, timeout=args.timeout)
    data = resp.get("data") or {}
    if data.get("status") == "confirmation_required":
        emit(args, resp)
        sys.exit(2)
    emit(args, resp)


def cmd_op(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    deadline = time.monotonic() + (args.wait if args.wait > 0 else 0)
    while True:
        resp = lc_call(sock, {"kind": "operation.status", "operation_id": args.operation_id}, timeout=args.timeout)
        status = (resp.get("data") or {}).get("status")
        if args.wait <= 0 or status != "pending" or time.monotonic() >= deadline:
            emit(args, resp)
            if status == "failed":
                sys.exit(1)
            return
        time.sleep(0.25)


def cmd_lc(args: argparse.Namespace) -> None:
    sock = resolve_lc_socket(args)
    intent = parse_json_arg(args.intent, "intent")
    address = parse_json_arg(args.address, "address") if args.address else None
    resp = lc_call(sock, intent, address=address, timeout=args.timeout)
    emit(args, resp)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    def add_common_args(target: argparse.ArgumentParser, suppress: bool) -> None:
        d = argparse.SUPPRESS if suppress else None
        target.add_argument(
            "--json",
            action="store_true",
            default=argparse.SUPPRESS if suppress else False,
            help="Output raw JSON",
        )
        target.add_argument(
            "--namespace",
            default=d,
            help="Ibudo namespace (default: IBUDO_NAMESPACE or Ibudo)",
        )
        target.add_argument("--socket", default=d, help="Override Unix socket path directly")
        target.add_argument(
            "--server",
            default=d,
            help="Target a connected remote Ibudo server by name (daemon commands)",
        )
        target.add_argument(
            "--timeout",
            type=float,
            default=argparse.SUPPRESS if suppress else 15.0,
            help="Socket timeout in seconds (default: 15)",
        )

    common_top = argparse.ArgumentParser(add_help=False)
    add_common_args(common_top, suppress=False)
    common = argparse.ArgumentParser(add_help=False)
    add_common_args(common, suppress=True)

    parser = argparse.ArgumentParser(
        prog="ibudo.py",
        description="Control Ibudo over its local Unix sockets (server.sock and c.sock).",
        parents=[common_top],
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Daemon commands
    p = sub.add_parser("ensure", parents=[common], help="Start or verify local IbudoServer headless")
    p.add_argument("--helper", help="Path to IbudoServer binary")
    p.set_defaults(func=cmd_ensure)

    p = sub.add_parser("hello", parents=[common], help="Ping IbudoServer (terminal protocol v3)")
    p.set_defaults(func=cmd_hello)

    p = sub.add_parser("servers", parents=[common], help="List local host and saved remote Ibudo servers")
    p.set_defaults(func=cmd_servers)

    p = sub.add_parser("session", parents=[common], help="Read saved session snapshot via session.exchange")
    p.add_argument("--lineage", action="store_true", help="Include databaseGeneration and resetCounter")
    p.set_defaults(func=cmd_session)

    p = sub.add_parser(
        "panes",
        parents=[common],
        help="List panes joined with live terminals (including SSH labels and connection IDs)",
    )
    p.add_argument("--filter", help="Case-insensitive substring filter (name, label, title, ID)")
    p.add_argument("--live-only", action="store_true", help="Only show panes with a currently running terminal")
    p.set_defaults(func=cmd_panes)

    p = sub.add_parser("terminals", parents=[common], help="List live terminals on IbudoServer")
    p.set_defaults(func=cmd_terminals)

    p = sub.add_parser(
        "read",
        parents=[common],
        help="Read terminal screen context without resizing (supports local and managed SSH panes)",
    )
    p.add_argument("terminal_id", help="Terminal ID, pane:<uuid>, pane UUID, or SSH connectionID")
    p.add_argument("--snapshot", action="store_true", help="Return raw ANSI snapshot instead of plain context")
    p.add_argument("--connection-id", help="Explicit managed SSH connectionID (optional)")
    p.add_argument("--generation", help="Explicit managed SSH generation (optional)")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser(
        "send",
        parents=[common],
        help="Send input bytes to an existing terminal (supports local and managed SSH panes)",
    )
    p.add_argument("terminal_id", help="Terminal ID, pane:<uuid>, pane UUID, or SSH connectionID")
    p.add_argument("text", nargs="?", help="Text to send (or pass --stdin)")
    p.add_argument("--stdin", action="store_true", help="Read input bytes from stdin")
    p.add_argument("--enter", action="store_true", help="Append carriage return (Enter)")
    p.add_argument("--if-at-prompt", action="store_true", help="Abort if busy or OSC 133 atPrompt is false")
    p.add_argument("--if-idle", action="store_true", help="Abort if busy or in alternate screen (works over SSH without OSC 133)")
    p.add_argument("--wait", type=float, default=0.0, help="Seconds to wait then read context/output after sending")
    p.add_argument(
        "--wait-prompt",
        action="store_true",
        help="Wait until prompt returns (or quiet idle if shell lacks OSC 133), bounded by --wait or --timeout",
    )
    p.add_argument(
        "--quiet",
        type=float,
        default=0.8,
        help="Idle quiet seconds fallback for --wait-prompt when shell lacks OSC 133 (default: 0.8)",
    )
    p.add_argument(
        "--capture",
        action="store_true",
        help="Capture ANSI-stripped PTY output stream while waiting instead of only the final viewport",
    )
    p.add_argument("--connection-id", help="Explicit managed SSH connectionID (optional)")
    p.add_argument("--generation", help="Explicit managed SSH generation (optional)")
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("spawn", parents=[common], help="Create a new headless hostDefaults terminal")
    p.add_argument("--id", help="Explicit terminalID (default: agent-<uuid>)")
    p.add_argument("--cwd", help="Initial working directory")
    p.add_argument("--cols", type=int, default=120)
    p.add_argument("--rows", type=int, default=40)
    p.add_argument("--recreate", action="store_true", help="Recreate a lost terminal ID")
    p.set_defaults(func=cmd_spawn)

    p = sub.add_parser("terminate", parents=[common], help="Terminate an ordinary terminal by ID")
    p.add_argument("terminal_id", help="Terminal ID or pane:<uuid>")
    p.set_defaults(func=cmd_terminate)

    p = sub.add_parser("run", parents=[common], help="Run a command in a fresh headless terminal")
    p.add_argument("command", help="Shell command to run")
    p.add_argument("--cwd", help="Initial working directory")
    p.add_argument("--id", help="Explicit terminalID")
    p.add_argument("--cols", type=int, default=120)
    p.add_argument("--rows", type=int, default=40)
    p.add_argument("--keep", action="store_true", help="Detach instead of terminating after completion")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("service", parents=[common], help="Call any Host Services v1 method")
    p.add_argument("method", help="Host service method name (e.g. files.list, ssh.profiles.list)")
    p.add_argument("payload", nargs="?", help="JSON object payload")
    p.add_argument("--raw", action="store_true", help="Print full service envelope including identity/revision")
    p.set_defaults(func=cmd_service)

    p = sub.add_parser("ports", parents=[common], help="Scan listening TCP ports on the host (ports.scan)")
    p.set_defaults(func=cmd_ports)

    p = sub.add_parser("activity", parents=[common], help="Read Ibudo activity history")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--category")
    p.add_argument("--severity")
    p.add_argument("--status")
    p.add_argument("--action-id")
    p.add_argument("--pane-id")
    p.set_defaults(func=cmd_activity)

    # Local control (c.sock) commands
    p = sub.add_parser("identify", parents=[common], help="Identify running Ibudo.app and current focus")
    p.set_defaults(func=cmd_identify)

    p = sub.add_parser("layout", parents=[common], help="Inspect Ibudo.app workspaces, tabs, and panes")
    p.add_argument("--workspace", help="Filter by concrete workspace ID or handle")
    p.add_argument("--tab", help="Filter by concrete tab ID or handle")
    p.set_defaults(func=cmd_layout)

    p = sub.add_parser("context", parents=[common], help="Read current Ibudo.app context snapshot")
    p.add_argument("--workspace")
    p.add_argument("--tab")
    p.add_argument("--pane")
    p.set_defaults(func=cmd_context)

    p = sub.add_parser("actions", parents=[common], help="List allowlisted Ibudo.app actions and schemas")
    p.add_argument("--filter", help="Substring filter on action ID or title")
    p.set_defaults(func=cmd_actions)

    p = sub.add_parser("ssh-profiles", parents=[common], help="List SSH profiles and active SSH panes")
    p.set_defaults(func=cmd_ssh_profiles)

    p = sub.add_parser("git-status", parents=[common], help="Read Git status for an Ibudo workspace tab")
    p.add_argument("--tab", help="Workspace tab handle or selector (default: tab:active)")
    p.set_defaults(func=cmd_git_status)

    p = sub.add_parser("search", parents=[common], help="Query Ibudo's command palette search")
    p.add_argument("query", help="Search string")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--tab", help="Workspace tab handle or selector (default: tab:active)")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("settings-get", parents=[common], help="Read one Ibudo setting and revision token")
    p.add_argument("setting", help="Setting key (e.g. terminal.profile.global.font_size)")
    p.set_defaults(func=cmd_settings_get)

    p = sub.add_parser("action", parents=[common], help="Run or check an allowlisted Ibudo.app action")
    p.add_argument("action_id", help="Action ID (see 'actions')")
    p.add_argument("payload", nargs="?", help="JSON object payload")
    p.add_argument("--workspace", help="Target workspace handle/ID or selector")
    p.add_argument("--tab", help="Target workspace tab handle/ID or selector")
    p.add_argument("--pane", help="Target pane handle/ID or selector")
    p.add_argument("--confirm", help="Single-use confirmation_token from a prior confirmation_required reply")
    p.add_argument("--background", action="store_true", help="Run async action in background")
    p.add_argument("--availability", action="store_true", help="Check availability without running")
    p.set_defaults(func=cmd_action)

    p = sub.add_parser("op", parents=[common], help="Check or poll an Ibudo.app background operation")
    p.add_argument("operation_id", help="Operation UUID")
    p.add_argument("--wait", type=float, default=0.0, help="Poll up to N seconds until finished")
    p.set_defaults(func=cmd_op)

    p = sub.add_parser("lc", parents=[common], help="Send a raw intent to c.sock")
    p.add_argument("intent", help="JSON object for intent")
    p.add_argument("--address", help="Optional JSON object for address")
    p.set_defaults(func=cmd_lc)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except IbudoError as exc:
        if getattr(args, "json", False) and exc.payload is not None:
            print(json.dumps(exc.payload, indent=2), file=sys.stderr)
        else:
            print(f"error: {exc}", file=sys.stderr)
        sys.exit(exc.exit_code)


if __name__ == "__main__":
    main()
