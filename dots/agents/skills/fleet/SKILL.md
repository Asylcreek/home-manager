---
name: fleet
description: Use when working on book, mini, pve, pve2, or pve3 choosing which machine should run a task, or coordinating work across these machines.
---

# Machines

1. book (this machine)
2. mini - accessible via `ssh mini`
3. pve - accessible via `ssh hl01`
4. pve2 - accessible via `ssh hl02`
5. pve3 - accessible via `ssh hl03`

## Book

- This is a Macbook Pro 16 M1 2021
- 16gb ram, 512gb ssd

## Mini

- This is a Mac Mini M4 Pro
- 24gb ram, 512gb ssd
- Jellyfin is running on it

## PVE

- This is an HP Elitedesk 800 G5 Mini
- 32gb ram, 256 nvme
- It's running proxmox

## PVE2

- This is an HP Elitedesk 800 G5 Mini
- 32gb ram, 256 nvme
- It's running proxmox

## PVE3

- This is a Dell Optiplex 7020, Core i7-4790
- 16gb ram, 500gb ssd
- 3 external hdds connected to it
- It's running proxmox
- It's supposed to be a NAS

## Connections

- book is mobile and can be connected to other networks
- mini, pve, pve2 and pve3 are always connected to the same network as they are stationary at home and connected to a 2.5gbe switch even as their ethernet NICs only negotiate 1gbe
- book, mini, pve are connected to Netbird; so when book is connected to a different network, it can still reach mini and pve, pve2, pve3 over Netbird
- pve, pve2, and pve3 are in a proxmox cluster with a qdevice installed in an orbstack machine on mini for quorum
