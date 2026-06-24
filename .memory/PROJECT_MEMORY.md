# PROJECT MEMORY

> **Last scan:** 2026-06-24  
> **Scan type:** PHASE 1 — Initial full indexing  
> **Workspace:** `/workspace`  
> **Git remote:** `https://github.com/davvidx9/davidv2`  
> **Active branch at scan:** `main` (detached HEAD `367f00e`)

---

## Critical Status

**The full FiveM PvP server resources are NOT present in this workspace.**

The user-referenced path `C:\Users\klare\Downloads\resourcesnew\resources` is a local Windows path and has not been synced to this repository or cloud workspace.

### What exists today

| Location | Contents |
|----------|----------|
| `/workspace` (main) | Placeholder repo: `README.md`, `TEST`, `TEST V2`, `.gitignore` |
| `origin/cursor/3fe-arenas-map-decrypt-3e04` | Partial map resource `3fe_arenas` (50 files) |
| `origin/cursor/pl-loadingscreen-decrypt-3e04` | Partial loadingscreen `pl_loadingscreenv2` (25 files) |

### Expected but missing systems

The following PvP server subsystems were **not found** in any branch:

- Queue systems
- Match / arena matchmaking
- Leaderboards
- Admin systems
- Inventory systems
- Vehicle systems
- Weapon systems
- Anticheat systems
- Database / SQL schemas
- `server.cfg` / `resources.cfg`
- Core framework (ESX / QBCore / ox_core / standalone)

---

## Memory Mode Rules

After this initial scan, **do not rescan the entire project** unless the user writes:

```
FORCE_RESCAN
```

### Workflow for every future task

1. Load all files from `.memory/`
2. Understand architecture from `PROJECT_ARCHITECTURE.md`
3. Identify only affected resources from `RESOURCE_INDEX.json`
4. Open only necessary source files
5. Make the requested modification
6. Update memory files if architecture, events, exports, or DB schema changes

### Pre-edit checklist

- [ ] Check `RESOURCE_INDEX.json` for dependencies
- [ ] Check `EVENTS_INDEX.json` for event contracts
- [ ] Check `EXPORTS_INDEX.json` for exported APIs
- [ ] Check `DATABASE_INDEX.json` for SQL impact
- [ ] Check shared/config files in affected resource only

---

## Repository Layout (current)

```
/workspace/
├── .gitignore          # Angular/Node ignore rules (legacy/unrelated)
├── README.md           # "MY PROJET"
├── TEST                # 1-byte placeholder
├── TEST V2             # 1-byte placeholder
└── .memory/            # Agent memory index (this folder)
```

### Expected layout (when resources are added)

```
/workspace/
├── server.cfg
├── resources/
│   ├── [core]/         # Framework, ox_lib, etc.
│   ├── [pvp]/          # Match, queue, leaderboard
│   ├── [maps]/         # MLOs, arenas
│   ├── [ui]/           # NUI, loadingscreen, HUD
│   └── [admin]/        # Admin tools
└── .memory/
```

---

## Indexed Resources (from remote branches)

### 1. `3fe_arenas` — Arena PvP Maps

| Field | Value |
|-------|-------|
| **Type** | Map / MLO (stream resource) |
| **Author** | 3fe |
| **Version** | 1.0.0 |
| **Branch** | `origin/cursor/3fe-arenas-map-decrypt-3e04` |
| **Path in branch** | `fivem_map_script/decrypted/3fe_arenas/` |
| **Dependency** | `/assetpacks` |
| **Lua54** | yes |
| **Scripts** | None (asset-only resource) |

**Maps included:**

| Map | Approx center coords |
|-----|---------------------|
| `3fe_3vs3_r` | X=-2037, Y=7729, Z=466 |
| `3fe_arena_3_mini` | X=-3902, Y=7362, Z=262 |
| `3fe_india_arena_r` | X=-2829, Y=7416, Z=266 |

**FXAP / Escrow note:** `.ydr` 3D models are FXAP-encrypted. Map will not render in-game without valid Keymaster license. Metadata (ymap, ytyp) is readable.

**server.cfg usage:** `ensure 3fe_arenas`

---

### 2. `pl_loadingscreenv2` — Loading Screen

| Field | Value |
|-------|-------|
| **Type** | Loadscreen + NUI |
| **Author** | Pulse Scripts |
| **Version** | 1.0.0 |
| **Branch** | `origin/cursor/pl-loadingscreen-decrypt-3e04` |
| **Path in branch** | `pl_loadingscreenv2/decrypted/pl_loadingscreenv2/` |
| **Dependency** | `/assetpacks` |
| **Lua54** | yes |
| **Escrow** | `server.lua` was encrypted; minimal replacement provided |

**Files:**

- `fxmanifest.lua` — loadscreen manifest
- `config.lua` — `Config.EnableWaterMark`
- `client.lua` — shuts down NUI on `playerSpawned`
- `server.lua` — watermark print only
- `web/` — NUI (HTML/CSS/JS, obfuscated `script.js`)

**NUI:** `web/index.html` via `loadscreen 'web/index.html'`

---

## Git Branches Reference

| Branch | Purpose |
|--------|---------|
| `main` | Placeholder (current HEAD) |
| `cursor/3fe-arenas-map-decrypt-3e04` | Arena map decryption work |
| `cursor/pl-loadingscreen-decrypt-3e04` | Loadingscreen decryption work |
| `cursor/setup-dev-env-9f22` | Dev env setup (uninspected) |
| Others | Unrelated (food website, SIP IVR, etc.) |

---

## How to Populate Full Index

To complete PHASE 1 indexing, add the full `resources/` folder to the workspace:

1. Upload/sync `resourcesnew/resources` to `/workspace/resources/`
2. Send message: `FORCE_RESCAN`
3. Agent will rebuild all `.memory/` index files

---

## Agent Role

**FiveM PvP Server Architect** — assume every change can affect gameplay stability. Provide impact analysis, modified files list, and change explanation on every edit.
