#!/usr/bin/env bash
# Vuelca por ADB el estado de seguridad de un Android a ficheros de texto (evidencias).
# Requiere: adb instalado y "Depuracion USB" activada en el movil.
# Uso: ./auditar_android.sh <modelo> <antes|despues>
set -euo pipefail
command -v adb >/dev/null || { echo "adb no instalado (ver README)."; exit 1; }
adb get-state >/dev/null 2>&1 || { echo "No hay movil conectado (adb devices)."; exit 1; }

MODELO="${1:-movil}"; ETIQUETA="${2:-antes}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/evidencias/movil/${MODELO}-${ETIQUETA}"
mkdir -p "$DEST"

vuelca() { echo "# $1"; adb shell "$2" 2>&1 || true; }   # titulo, comando

{
  vuelca "A2 root (su debe estar vacio)"            "which su"
  vuelca "A2 verified boot (green) / bootloader (1)" "getprop ro.boot.verifiedbootstate; getprop ro.boot.flash.locked"
  vuelca "A3 parche de seguridad"                   "getprop ro.build.version.security_patch"
  vuelca "A3 version de Android"                    "getprop ro.build.version.release"
  vuelca "A4 redes wifi guardadas"                  "cmd wifi list-networks"
  vuelca "A4 redes con SSID oculto (HIDDEN: true)"  "dumpsys wifi | grep -oE 'SSID: \"[^\"]*\" .*HIDDEN: true' | sed -E 's/(SSID: \"[^\"]*\").*/\\1/' | sort -u"
  vuelca "A5 bluetooth (0 = apagado)"               "settings get global bluetooth_on"
  vuelca "B1 apps de terceros y quien las instalo"  "pm list packages -3 -i"
  vuelca "B3 servicios de accesibilidad"            "settings get secure enabled_accessibility_services"
  vuelca "B3 lectores de notificaciones"            "settings get secure enabled_notification_listeners"
  vuelca "B3 permiso de superposicion (overlay)"    "cmd appops query-op SYSTEM_ALERT_WINDOW allow"
  vuelca "B3 acceso total a almacenamiento"         "cmd appops query-op MANAGE_EXTERNAL_STORAGE allow"
  vuelca "B3 apps de terceros con lectura de almacenamiento concedida" "for p in \$(pm list packages -3 | cut -d: -f2); do dumpsys package \$p 2>/dev/null | grep -q 'READ_EXTERNAL_STORAGE: granted=true' && echo \$p; done"
  vuelca "Extra cifrado"                            "getprop ro.crypto.state"
} | tee "$DEST/auditoria.txt"

echo
echo "Evidencia guardada en $DEST/auditoria.txt"
