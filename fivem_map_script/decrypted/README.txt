3fe_arenas - FiveM Map Decryption Report
=========================================

Resource: 3fe_arenas
Author: 3fe
Type: Arena PvP Maps (MLO/YMAP)

DOWNLOADED: 2.43 MB zip from Google Drive

FILE STATUS:
------------

READABLE (not FXAP encrypted):
  ✓ fxmanifest.lua

PARTIALLY READABLE (RSC7 format - placement/type data):
  ✓ stream/3fe_3vs3_r.ymap
  ✓ stream/3fe_arena_3_mini.ymap
  ✓ stream/3fe_india_arena_r.ymap
  ✓ stream/3fe_arenas.ytyp
  ✓ stream/3fe_3vs3_r.ytyp
  ✓ stream/3fe_india_r.ytyp
  ✓ stream/_manifest.ymf

ENCRYPTED - CANNOT DECRYPT without CFX Keymaster license:
  ✗ stream/3fe_3vs3_r.ydr         (626 KB - 3D model)
  ✗ stream/3fe_arena_3_mini.ydr (1.1 MB - 3D model)
  ✗ stream/3fe_india_arena_r.ydr (626 KB - 3D model)
  ✗ .fxap                        (escrow license file)

IMPORTANT:
----------
The .YDR files are the 3D map models. Without them the map WILL NOT
appear in-game. They are protected by FiveM Asset Escrow (FXAP).

To use this map you MUST:
1. Own it on your CFX Keymaster account
2. Use your server's license key linked to the purchase
3. Upload the ORIGINAL zip to your server (not FileZilla - use WinSCP)

MAPS INCLUDED:
--------------
1. 3fe_3vs3_r        - 3v3 Arena
2. 3fe_arena_3_mini  - Mini Arena
3. 3fe_india_arena_r - India Arena

EXTRACTED MAP POSITIONS (from .ymap):
-------------------------------------
3fe_3vs3_r:
  Approx: X=-2100, Y=7600, Z=266-472

3fe_arena_3_mini:
  Approx: X=-3500, Y=7600, Z=262-678

3fe_india_arena_r:
  Approx: X=-2650, Y=7550, Z=266-472

Created with CodeWalker (Aug 2024)

INSTALL (with valid license):
-----------------------------
1. Copy 3fe_arenas folder to resources/
2. server.cfg: ensure 3fe_arenas
3. Requires: dependency '/assetpacks'

fxmanifest.lua content:
-----------------------
fx_version 'bodacious'
game 'gta5'
data_file 'DLC_ITYP_REQUEST' for ytyp files
dependency '/assetpacks'
