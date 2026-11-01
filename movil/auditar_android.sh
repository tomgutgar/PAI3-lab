#!/usr/bin/env bash
# Vuelca por ADB el estado de seguridad de un Android a ficheros de texto (evidencias).
# Uso: ./auditar_android.sh <modelo> <antes|despues>
set -euo pipefail
MODELO="${1:-movil}"; ETIQUETA="${2:-antes}"
DEST="$(dirname "$0")/../evidencias/movil/${MODELO}-${ETIQUETA}"
mkdir -p "$DEST"
ADB='adb shell'

# A2 root / verified boot
$ADB which su                                   > "$DEST/root_su.txt" 2>&1 || true
$ADB getprop ro.boot.verifiedbootstate          > "$DEST/verifiedboot.txt" 2>&1 || true
$ADB getprop ro.boot.flash.locked               >> "$DEST/verifiedboot.txt" 2>&1 || true
# A3 parche de seguridad
$ADB getprop ro.build.version.security_patch     > "$DEST/security_patch.txt" 2>&1 || true
# A4 redes wifi guardadas
$ADB cmd wifi list-networks                      > "$DEST/wifi.txt" 2>&1 || true
# A5 bluetooth
$ADB settings get global bluetooth_on            > "$DEST/bluetooth.txt" 2>&1 || true
# B1 apps de terceros y quién las instaló
$ADB pm list packages -3 -i                      > "$DEST/apps_terceros.txt" 2>&1 || true
# B3 permisos peligrosos
$ADB settings get secure enabled_accessibility_services   > "$DEST/accesibilidad.txt" 2>&1 || true
$ADB settings get secure enabled_notification_listeners    > "$DEST/notif_listeners.txt" 2>&1 || true
$ADB cmd appops query-op SYSTEM_ALERT_WINDOW allow         > "$DEST/overlay.txt" 2>&1 || true
# cifrado
$ADB getprop ro.crypto.state                     > "$DEST/cifrado.txt" 2>&1 || true

echo "Evidencias en $DEST"
