# Fin thot cookies dyal account dyalek

## Blasa dial cookies

**File:** `cookies.json` (f nafs dossier dyal `fill_payment_form.py`)

Hiya hiya blasa li kat7ot fiha cookies dyal account mconnecté.

Ila `cookies.json` ma kaynach, script ghadi ycreyiha automatiquement mn `cookies.template.json`.

---

## Kifach tjib cookies mn browser

### 1) Connecté f SignalWire

1. Fta7 Chrome
2. Dkhol l: `https://us11111111.signalwire.com`
3. Connecté b account dyalek

### 2) Export cookies

**Option A — DevTools (Chrome):**

1. `F12` → tab **Application**
2. Mn lisère khelli: **Storage → Cookies → https://us11111111.signalwire.com**
3. Copier kol cookie li kayn (smiya + value)
4. Zidhom f `cookies.json`

**Option B — Extension:**

- Installi extension b7al **Cookie-Editor** wla **EditThisCookie**
- Export cookies b format **JSON**
- Copier kolchi w paste f `cookies.json`

---

## Kifach t3mer `cookies.json`

Fta7 file `cookies.json` w bdel ghir `value` (w `name` ila ma matl9ach):

```json
[
  {
    "name": "_signalwire_session",
    "value": "PASTE_VALUE_HNA",
    "domain": ".signalwire.com",
    "path": "/",
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  }
]
```

- **`name`** = smiya dial cookie (mn DevTools)
- **`value`** = **HNA fin katpaste value dyal session** ← hadchi lmohem
- **`domain`** = `.signalwire.com` wla `us11111111.signalwire.com`

> **Note:** Ila jbti cookies mn Chrome extension, `sameSite` kaykon `unspecified` — script kayfixih automatiquement. Ma khassk tbeddlou.

Ila 3andek bzaf dial cookies, zid object jdid f liste:

```json
[
  { "name": "cookie1", "value": "...", "domain": ".signalwire.com", "path": "/" },
  { "name": "cookie2", "value": "...", "domain": "us11111111.signalwire.com", "path": "/" }
]
```

---

## Verifier

Men ba3d ma t7ot cookies:

```bash
python fill_payment_form.py
```

Ila session valid → ghadi ymchi l page dial payment.
Ila invalid → screenshot f `screenshots/` + error f console.

---

## Sécurité

- **Ma tpartagih `cookies.json` ma3a hta wa7ed** — kayn fih session dyalek
- File déjà f `.gitignore` — ma ghadi ytupload l GitHub
