#!/usr/bin/env bash
# Bastionado para Debian/Ubuntu. Idempotente: se puede ejecutar varias veces.
# Aplica medidas por grupos; entre grupos, vuelve a pasar run_lynis.sh para medir.
# Uso: sudo ./hardening.sh            (todas)
#      sudo ./hardening.sh firewall   (solo un grupo)
# ponytail: solo apt/Debian-Ubuntu; en Fedora cambia apt->dnf y las rutas.
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecuta con sudo."; exit 1; }
DIR="$(dirname "$0")"
export DEBIAN_FRONTEND=noninteractive   # aide/rkhunter tiran de postfix, que pregunta

# Añade una línea a un fichero solo si no está ya (idempotencia).
anadir() { grep -qxF "$2" "$1" 2>/dev/null || echo "$2" >> "$1"; }

firewall() {           # FIRE-4590
  apt-get install -y ufw
  ufw default deny incoming; ufw default allow outgoing; ufw --force enable
}
passwords() {          # AUTH-9262 (robustez) + AUTH-9286 (caducidad) + AUTH-9328 (umask)
  apt-get install -y libpam-pwquality
  anadir /etc/security/pwquality.conf "minlen = 12"
  anadir /etc/security/pwquality.conf "dcredit = -1"
  anadir /etc/security/pwquality.conf "ucredit = -1"
  sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs
  sed -i 's/^PASS_WARN_AGE.*/PASS_WARN_AGE   7/'  /etc/login.defs
  sed -i 's/^UMASK.*/UMASK           027/'        /etc/login.defs
}
banner() {             # BANN-7126 / BANN-7130
  local T="Acceso restringido a personal autorizado. Toda actividad queda registrada."
  echo "$T" > /etc/issue; echo "$T" > /etc/issue.net
}
usb() {                # STRG-1840 / STRG-1846
  cat > /etc/modprobe.d/disable-usb-storage.conf <<'E2'
install usb-storage /bin/true
install firewire-core /bin/true
E2
}
kernel() {             # KRNL-6000
  cp "$DIR/sysctl-hardening.conf" /etc/sysctl.d/99-hardening.conf
  sysctl --system >/dev/null
}
coredumps() {          # KRNL-5820
  anadir /etc/security/limits.conf "* hard core 0"
}
herramientas() {       # ACCT-*, HRDN-7230, FINT-4350, DEB-0880, PKGS-7394
  apt-get install -y auditd acct sysstat rkhunter fail2ban apt-show-versions aide
}

TODOS=(firewall passwords banner usb kernel coredumps herramientas)
apt-get update
if [ $# -gt 0 ]; then "$1"; else for g in "${TODOS[@]}"; do echo ">> $g"; "$g"; done; fi
echo "Hecho. Vuelve a pasar run_lynis.sh para ver el nuevo hardening index."
