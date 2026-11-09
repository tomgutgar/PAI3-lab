#!/usr/bin/env bash
# Punto B2: lista las conexiones TCP establecidas del movil y la app que tiene cada una.
# Se ejecuta con el navegador corporativo (Chrome) abierto y en uso.
# Lee /proc/net/tcp y tcp6 (el UID de cada conexion) y lo cruza con "pm list packages -U".
# Uso: ./conexiones_b2.sh <modelo> <antes|despues>
set -euo pipefail
command -v adb >/dev/null || { echo "adb no instalado (ver README)."; exit 1; }
adb get-state >/dev/null 2>&1 || { echo "No hay movil conectado (adb devices)."; exit 1; }

MODELO="${1:-movil}"; ETIQUETA="${2:-antes}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/evidencias/movil/${MODELO}-${ETIQUETA}"
mkdir -p "$DEST"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

adb shell "cat /proc/net/tcp /proc/net/tcp6" > "$TMP/tcp" 2>&1 || true
adb shell "pm list packages -U" > "$TMP/uids" 2>&1 || true

python3 -I - "$TMP/tcp" "$TMP/uids" <<'EOF' | tee "$DEST/conexiones-b2.txt"
import sys, socket, struct, datetime
tcp, uids = open(sys.argv[1]).read().splitlines(), open(sys.argv[2]).read().splitlines()
apps = {}
for l in uids:                      # package:com.android.chrome uid:10123
    if l.startswith("package:") and " uid:" in l:
        pkg, uid = l[8:].split(" uid:")
        for u in uid.split(","):
            apps.setdefault(int(u), []).append(pkg)

def ip(h):                          # direccion en hex little-endian -> texto
    b = bytes.fromhex(h)
    if len(b) == 4:
        return socket.inet_ntoa(b[::-1])
    b = b"".join(b[i:i+4][::-1] for i in range(0, 16, 4))
    if b[:12] == b"\0" * 10 + b"\xff\xff":           # IPv4 dentro de IPv6
        return socket.inet_ntoa(b[12:])
    return socket.inet_ntop(socket.AF_INET6, b)

def nombre(uid):
    if uid in apps: return ",".join(sorted(apps[uid]))
    if uid >= 10000: return f"uid {uid} (app sin paquete listado)"
    return {0: "root (sistema)", 1000: "system (sistema)", 1051: "dns (sistema)"}.get(uid, f"uid {uid} (sistema)")

print(f"# B2 conexiones TCP establecidas ({datetime.datetime.now():%Y-%m-%d %H:%M})")
filas = []
for l in tcp:
    c = l.split()
    if len(c) < 8 or c[0] == "sl" or c[3] != "01":   # 01 = ESTABLISHED
        continue
    rip, rport = c[2].split(":")
    filas.append((nombre(int(c[7])), f"{ip(rip)}:{int(rport, 16)}"))
if not filas:
    print("Sin conexiones o /proc/net no accesible. Salida cruda:")
    print("\n".join(tcp[:5]))
for app, dst in sorted(filas):
    print(f"{app:55} -> {dst}")
print(f"\nTotal: {len(filas)} conexiones; apps distintas: {len({a for a,_ in filas})}")
EOF
echo
echo "Evidencia guardada en $DEST/conexiones-b2.txt"
