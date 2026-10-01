# 🔐 TOTP Authenticator

A lightweight, self-hosted two-factor authentication (2FA) app built with **Flask** and vanilla **HTML/CSS/JavaScript**. It generates time-based one-time passwords (TOTP) compatible with Google Authenticator, Authy, Microsoft Authenticator, and any service that follows [RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238).

The TOTP algorithm is implemented from scratch using only Python's standard library (`hmac`, `hashlib`, `struct`) — no third-party OTP packages required.

---

## ✨ Features

- **RFC 6238 / RFC 4226 compliant** TOTP generation (HMAC-SHA1, 30-second period, 6 digits)
- **Add accounts by QR code** — scan an `otpauth://` QR code using your device camera (via [html5-qrcode](https://github.com/mebjas/html5-qrcode))
- **Add accounts manually** — enter an account name and base32 secret key
- **Secret validation** — secrets are verified before being saved
- **Live countdown timer** with a progress bar showing time left in the current code window
- **Urgency indicator** — digits pulse red as the code is about to expire
- **One-click copy** to clipboard
- **Delete accounts** with a confirmation prompt
- **Modern dark UI** — responsive, minimal, no frontend build step
- **Persistent storage** — accounts are saved in the browser's `localStorage`

---

## 🛠️ Tech Stack

| Layer     | Technology                                   |
|-----------|----------------------------------------------|
| Backend   | Python 3, Flask ≥ 3.0                        |
| Frontend  | HTML5, CSS3, vanilla JavaScript              |
| QR Scan   | html5-qrcode 2.3.8 (loaded from CDN)         |
| Algorithm | TOTP (RFC 6238) over HOTP (RFC 4226)         |

---

## 📁 Project Structure

```
.
├── app.py              # Flask backend + TOTP implementation
├── requirements.txt    # Python dependencies
└── templates/
    └── index.html      # Single-page frontend (HTML + CSS + JS)
```

> **Note:** Flask's `render_template` looks for HTML files in a `templates/` folder, so make sure `index.html` is placed there.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or newer
- `pip`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Make sure index.html is inside a templates/ folder
mkdir -p templates
mv index.html templates/        # skip if already there
```

### Run the app

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

---

## 📖 Usage

1. Click the **+** button in the top-right corner (or the "Add an account" link on the empty screen).
2. Choose how to add an account:
   - **Scan QR Code** — allow camera access and point it at the QR code shown by the service you're enabling 2FA for.
   - **Enter Manually** — type an account name and the base32 secret key provided by the service.
3. Your account appears with a live 6-digit code that refreshes every 30 seconds.
4. Click **Copy** to copy the current code to your clipboard.
5. Hover over a card and click the trash icon to delete an account.

> 📷 Camera access in browsers requires a secure context — it works on `localhost` and over HTTPS.

---

## 🔌 API Reference

### `POST /api/generate`

Generate TOTP codes for one or more accounts.

**Request**
```json
{
  "accounts": [
    { "id": "abc-123", "secret": "JBSWY3DPEHPK3PXP" }
  ]
}
```

**Response**
```json
{
  "codes": { "abc-123": "123456" },
  "time_remaining": 17
}
```

Accounts with an invalid secret return `"ERROR"` in place of a code.

### `POST /api/validate_secret`

Check that a base32 secret can produce a valid TOTP code.

**Request**
```json
{ "secret": "JBSWY3DPEHPK3PXP" }
```

**Response (200)**
```json
{ "valid": true, "code": "123456" }
```

**Response (400)**
```json
{ "valid": false, "error": "Invalid base32 secret" }
```

---

## 🧠 How It Works

1. The shared secret (base32) is decoded into raw bytes.
2. The current Unix time is divided by the period (30s) to produce a counter.
3. The counter is packed as an 8-byte big-endian integer and signed with **HMAC-SHA1** using the secret.
4. **Dynamic truncation** extracts a 31-bit integer from the hash, which is reduced modulo `10^6` to produce the 6-digit code.

---

## ⚠️ Security Notice

This project is intended for **learning, personal use, and experimentation**. Before using it for anything sensitive, please be aware:

- **Secrets are stored in plaintext in the browser's `localStorage`**, so anyone with access to the browser profile can read them.
- **Secrets are sent to the backend** on every code refresh. Only run this over HTTPS (or locally) and only on a server you fully trust.
- The app has **no authentication or user accounts**.
- `debug=True` is enabled in `app.py` — **disable it in production**.
- There is no backup/export feature; clearing browser data will delete your accounts.

For production deployments, consider generating codes client-side, encrypting stored secrets, adding authentication, and serving through a production WSGI server such as Gunicorn behind HTTPS.

---

## 🗺️ Roadmap Ideas

- [ ] Client-side TOTP generation (so secrets never leave the browser)
- [ ] Encrypted storage / master password
- [ ] Import / export accounts
- [ ] Support for SHA-256 / SHA-512, 8-digit codes, and custom periods
- [ ] Edit account names and reorder accounts
- [ ] Dockerfile

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). *(Add a `LICENSE` file to your repository.)*
