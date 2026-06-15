# Kifach ttesti (Windows) — double-click run.bat

## 1) Download mn GitHub

Clone wla download ZIP:

**Branch:** https://github.com/davvidx9/DAVIDV2/tree/cursor/signalwire-form-fill-eb58

```bash
git clone -b cursor/signalwire-form-fill-eb58 https://github.com/davvidx9/DAVIDV2.git
cd DAVIDV2
```

## 2) 3mer account dyalek (marra wa7da)

Fta7 `config.json` (ila ma kaynach, `run.bat` ghadi ycreyih) w beddel:

```json
"account": {
  "email": "email dyalek hna",
  "password": "password dyalek hna"
}
```

## 3) Double-click `run.bat`

`run.bat` kaydir kolchi automatiquement:

1. Install Python packages
2. Install Chromium (Playwright)
3. Create config ila ma kaynach
4. Fta7 browser (tab)
5. Login l account
6. Mchi l page dial billing
7. 3mer form
8. Browser kaybqa ma7loul — review w press ENTER

## 4) Ila kan chi mochkil

- Chouf `automation.log`
- Chouf screenshots f `screenshots/`
- Verifier email/password f `config.json`

## 5) Men ba3d ma ttesti

Goliya wach khdam w nkmlo l khota l akher (submit, selectors, etc.)
