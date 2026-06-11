3fe_arenas - FiveM Map Resource Analysis
=========================================

Resource: 3fe_arenas
Author: 3fe
Type: Arena PvP Maps (YMAP/YDR)
Source: https://drive.google.com/file/d/1oTLtbMPUmfugPRiGfL-8y77FZrcAOGpQ/view

---

RESULTAT / RESULT / النتيجة
---------------------------

Les fichiers .YDR (modeles 3D) sont CHIFFRES avec FXAP (Asset Escrow FiveM).
Impossible de les dechiffrer sans licence Keymaster valide.

The .YDR files (3D models) are ENCRYPTED with FXAP (FiveM Asset Escrow).
Cannot be decrypted without a valid Keymaster license.

ملفات .YDR (الموديلات 3D) مشفرة بـ FXAP. مايمكنش فك التشفير بلا licence Keymaster.

---

FILE STATUS / ETAT DES FICHIERS
-------------------------------

READABLE (extracted successfully):
  ✓ fxmanifest.lua
  ✓ stream/3fe_3vs3_r.ymap
  ✓ stream/3fe_arena_3_mini.ymap
  ✓ stream/3fe_india_arena_r.ymap
  ✓ stream/3fe_arenas.ytyp
  ✓ stream/3fe_3vs3_r.ytyp
  ✓ stream/3fe_india_r.ytyp
  ✓ stream/_manifest.ymf
  ✓ map_data.json (extracted coordinates)

ENCRYPTED (FXAP - cannot decrypt):
  ✗ stream/3fe_3vs3_r.ydr         (626 KB - 3D model)
  ✗ stream/3fe_arena_3_mini.ydr   (1.1 MB - 3D model)
  ✗ stream/3fe_india_arena_r.ydr  (626 KB - 3D model)
  ✗ .fxap                        (escrow license file)

---

MAPS INCLUDED / LES MAPS
------------------------

1. 3fe_3vs3_r        - Arena 3v3
   Position: X=-2037, Y=7729, Z=466

2. 3fe_arena_3_mini  - Mini Arena
   Position: X=-3902, Y=7362, Z=262

3. 3fe_india_arena_r - India Arena
   Position: X=-2829, Y=7416, Z=266

Created with CodeWalker (August 2024)

---

HOW TO USE / KIFACH TSTAKHDAM
-----------------------------

Option 1 - You OWN the map on Keymaster (recommended):
  1. Download original from your CFX account
  2. Copy 3fe_arenas folder to resources/
  3. server.cfg: ensure 3fe_arenas
  4. Upload as ZIP and extract on server (use WinSCP, NOT FileZilla)
  5. Requires: dependency '/assetpacks'

Option 2 - You DON'T own the map:
  The map will NOT work. The .YDR 3D models are required for the map
  to appear in-game. Only metadata (positions, types) was extracted.

---

FOLDER STRUCTURE
----------------

fivem_map_script/
  original/3fe_arenas/     - Original encrypted files from Google Drive
  extracted/3fe_arenas/    - Readable files only (no .fxap)
  decrypted/
    README.txt             - This file
    map_data.json          - Extracted map coordinates
    3fe_arenas/            - Full copy with encrypted .ydr files
