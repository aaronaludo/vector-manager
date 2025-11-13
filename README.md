# vector-manager

## FastAPI Art Protection

The `fastapi-art-protection` service now exposes an upload endpoint that embeds both an invisible spread-spectrum watermark and an encrypted watermark identifier before persisting asset metadata.

### Configuration

Set `WATERMARK_ENCRYPTION_KEY` in `fastapi-art-protection/.env` to a Fernet key:

```bash
python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
```

### Uploading protected images

`POST /protection/upload`

Form fields:

- `image`: PNG/JPEG/WebP file (required)
- `metadata`: JSON object encoded as a string (optional)
- `google_drive_url`: optional URL reference supplied by the user

Response contains the stored asset identifiers plus a base64-encoded copy of the watermarked image; the service does **not** persist the original upload.

- A watermarked PNG is written to `fastapi-art-protection/static/protected/<uuid>.png`, and FastAPI serves it at `/static/protected/<uuid>.png`. The `image_link` field points to that path so the protected file can be accessed directly once the app is running.
