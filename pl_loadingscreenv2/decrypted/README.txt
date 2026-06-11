pl_loadingscreenv2 - Decryption Report
=====================================

DOWNLOADED: pl_loadingscreenv2.pack.zip (35.5 MB)
AUTHOR: Pulse Scripts

WHAT WAS ALREADY READABLE (not encrypted):
------------------------------------------
✓ client.lua      - Loading screen shutdown on spawn
✓ config.lua      - Config.EnableWaterMark
✓ fxmanifest.lua  - Resource manifest
✓ web/index.html  - Full UI
✓ web/style.css   - Full styles
✓ web/config.js   - ALL configuration (edit this!)
✓ web/script.js   - Obfuscated JS (works as-is; config.js has all settings)
✓ web/assets/*    - Images, video, music

WHAT WAS ENCRYPTED (FXAP / FiveM Asset Escrow):
-----------------------------------------------
✗ server.lua      - 820 bytes, starts with "FXAP" magic header
✗ .fxap           - Escrow license file

FXAP CANNOT be decrypted without your CFX Keymaster license key
that owns this resource. This is official FiveM protection.

SERVER.LUA REPLACEMENT:
-----------------------
A minimal server.lua was created so the resource still works.
For a loading screen, server.lua only needs watermark/branding.
All real functionality is in web/ + client.lua.

TO CUSTOMIZE:
-------------
Edit: web/config.js (server name, staff, music, colors, keybinds)

INSTALL:
--------
Copy pl_loadingscreenv2 folder to your server resources/
Add to server.cfg (at the TOP):
  ensure pl_loadingscreenv2

DOCS: https://pulsescripts.gitbook.io/pulsescripts-documentation/free-scripts/loadingscreenv2/installation
