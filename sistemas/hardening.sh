#!/usr/bin/env bash
# Medidas de bastionado. Aplicar por GRUPOS y re-escanear para medir el efecto.
# Cada bloque está comentado: descomentar lo que se decida aplicar y justificarlo en el informe.
# Ver la tabla completa en la guía (sección 3).
set -euo pipefail

# --- Firewall (FIRE-4590) ---
# apt install -y ufw && ufw default deny incoming && ufw default allow outgoing && ufw --force enable

# --- Contraseñas robustas (AUTH-9262) ---
# apt install -y libpam-pwquality
# TODO: editar /etc/security/pwquality.conf (minlen=12, dcredit=-1, ucredit=-1, ...)

# --- Caducidad de contraseñas (AUTH-9286) + umask (AUTH-9328) en /etc/login.defs ---
# sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS 90/' /etc/login.defs
# sed -i 's/^UMASK.*/UMASK 027/' /etc/login.defs

# --- Banner legal (BANN-7126/7130) ---
# echo 'Acceso restringido. Uso autorizado unicamente.' | tee /etc/issue /etc/issue.net

# --- Bloquear USB/FireWire storage (STRG-1840/1846) ---
# echo 'install usb-storage /bin/true' > /etc/modprobe.d/disable-usb-storage.conf

# --- auditd / acct / sysstat (ACCT-*) ---
# apt install -y auditd acct sysstat

# --- rkhunter / aide / fail2ban / apt-show-versions ---
# apt install -y rkhunter aide fail2ban apt-show-versions

# --- Parámetros del kernel (KRNL-6000) ---
# cp sysctl-hardening.conf /etc/sysctl.d/99-hardening.conf && sysctl --system

echo 'Revisa y descomenta las medidas que vayas a aplicar.'
