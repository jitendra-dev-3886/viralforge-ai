Local quantized model setup (secure, minimal)
=============================================

1) Create models folder (Windows PowerShell):

```
New-Item -ItemType Directory -Path C:\models -Force
icacls C:\models /inheritance:r
icacls C:\models /grant "${env:USERNAME}:(OI)(CI)F"
icacls C:\models /grant "Administrators:F"
icacls C:\models /remove Everyone
```

2) Download a quantized ggml 7B model (e.g. `ggml-vicuna-7b-q4_0.bin`) from a trusted source and place it in `C:\models`.

3) Verify checksum (PowerShell):

```
CertUtil -hashfile C:\models\model-file.bin SHA256
```

4) Create Python venv and install runtime:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install llama-cpp-python
```

5) Run the test script:

```
python backend\test_llama.py
```

Security notes:
- Run inference as a non-admin user or inside a VM/WSL2.
- Mount models read-only if serving (Docker `:ro`).
- Bind any server to `127.0.0.1` and/or use `--network=none` in Docker.
- Keep model files in `C:\models` with restricted ACLs.
