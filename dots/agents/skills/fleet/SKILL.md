---
name: fleet
description: Machine directory for book, mini, pve, pve2, and pve3. Use when the user refers to one of these machines by name to identify what it is, which host you are on, and how to reach it.
---

Run `hostname` first to check which machine you are currently on.

## Machines

| Name | Hostname | SSH | Hardware and notes |
| --- | --- | --- | --- |
| `book` | `asyl-book` | `ssh book` | MacBook Pro 16 M1 2021, 16 GB RAM, 512 GB SSD |
| `mini` | `asyl` | `ssh mini` | Mac Mini M4 Pro, 24 GB RAM, 512 GB SSD, runs Jellyfin and Proxmox qdevice in OrbStack |
| `pve` | `pve` | `ssh hl01` | HP EliteDesk 800 G5 Mini, 32 GB RAM, 256 GB NVMe, Proxmox |
| `pve2` | `pve2` | `ssh hl02` | HP EliteDesk 800 G5 Mini, 32 GB RAM, 256 GB NVMe, Proxmox |
| `pve3` | `pve3` | `ssh hl03` | Dell Optiplex 7020, Core i7-4790, 16 GB RAM, 500 GB SSD, 3 external HDDs, Proxmox, NAS |

## Connections

- `book` is mobile and may be on other networks.
- `mini`, `pve`, `pve2`, and `pve3` stay at home on the same LAN through a 2.5GbE switch, with NICs negotiating 1GbE.
- `book`, `mini`, and `pve` are on Netbird. `book` and `mini` can reach each other and `pve`, `pve2`, and `pve3` over both LAN and Netbird.
- `pve`, `pve2`, and `pve3` form a Proxmox cluster using the qdevice in an OrbStack machine on `mini` for quorum.
