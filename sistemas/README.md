# Parte 1 — Auditoría de sistemas (Lynis) · Persona 1

> Objetivo: auditar **2-3 equipos Linux** con Lynis y bastionarlos hasta un **hardening index ≥ 70**, justificando en el informe cada medida que apliques (y por qué descartas otras).

## Qué necesitas saber antes de empezar

- **Bastionar (hardening)** = poner el sistema más seguro quitando lo que sobra y endureciendo la configuración.
- **Lynis** es un programa que revisa cientos de puntos de un Linux y te da una nota de 0 a 100 (el *hardening index*). **No cambia nada**: solo mira y te sugiere qué mejorar. Eres tú quien aplica los cambios.
- Cada sugerencia trae un código, p. ej. `AUTH-9262`. Si no entiendes una, búscala en https://cisofy.com/lynis/controls/ .
- Resultados: `[OK]` = bien; `[WARNING]` = revisar; `[NOT FOUND]` = no existe eso en el sistema.

## Paso 0 — Montar las máquinas (una tarde)

1. Instala **VirtualBox** (gratis).
2. Crea 2-3 máquinas virtuales con distros distintas (quedan mejor en el informe): p. ej. **Ubuntu 24.04**, **Debian 12**, **Fedora**.
3. En cada una: `sudo apt update && sudo apt upgrade -y` (en Fedora `sudo dnf upgrade`).
4. **Haz un snapshot** de cada VM (menú de VirtualBox → Instantáneas). Si algo se rompe al bastionar, vuelves atrás en un clic.

> No uses WSL: no tiene arranque ni kernel propios y Lynis da resultados raros.

## Paso 1 — Primer escaneo ("antes")

En cada máquina:

```bash
# Instala la ÚLTIMA versión (la de apt es vieja y resta puntos)
git clone https://github.com/CISOfy/lynis
cd lynis
sudo ./lynis audit system
```

Apunta el **hardening index** que sale al final. Copia los dos logs a las evidencias (lo hace el script):

```bash
sudo ../sistemas/run_lynis.sh antes   # ajusta la ruta a donde tengas el repo
```

Esto guarda `lynis.log` y `report.dat` en `evidencias/sistemas/`. **Guárdalos siempre**: Lynis los sobrescribe en cada pasada.

## Paso 2 — Leer qué mejorar

```bash
grep -E 'suggestion|warning' /var/log/lynis-report.dat
```

Haz una tabla (va al informe): código del test · qué dice · ¿lo aplico? · por qué.

## Paso 3 — Aplicar medidas y volver a escanear

Aplica las medidas **por grupos pequeños** y vuelve a pasar `run_lynis.sh` para ver cuánto sube cada grupo. Las que más suben:

| Medida | Test | Cómo |
|--------|------|------|
| Firewall | FIRE-4590 | `sudo apt install ufw && sudo ufw default deny incoming && sudo ufw enable` |
| Contraseñas robustas | AUTH-9262 | `sudo apt install libpam-pwquality`, editar `/etc/security/pwquality.conf` (minlen=12) |
| Caducidad de contraseñas | AUTH-9286 | `/etc/login.defs`: `PASS_MAX_DAYS 90`, `PASS_WARN_AGE 7` |
| umask estricto | AUTH-9328 | `/etc/login.defs`: `UMASK 027` |
| Banner legal | BANN-7126/7130 | Texto de aviso en `/etc/issue` y `/etc/issue.net` |
| Bloquear USB storage | STRG-1840 | `echo 'install usb-storage /bin/true' > /etc/modprobe.d/usb.conf` |
| Parámetros del kernel | KRNL-6000 | Fichero en `/etc/sysctl.d/` con lo que sugiera el log + `sudo sysctl --system` |
| auditd / sysstat | ACCT-* | `sudo apt install auditd acct sysstat` |
| Antirootkits | HRDN-7230 | `sudo apt install rkhunter` |
| Fuerza bruta | DEB-0880 | `sudo apt install fail2ban` |

El fichero `hardening.sh` tiene estas medidas comentadas: descomenta lo que decidas aplicar.

## Paso 4 — Escaneo final ("después") y repetir

```bash
sudo ../sistemas/run_lynis.sh despues
```

Repite en la máquina 2 (y 3) hasta llegar a **≥ 70** en todas. Si una no llega, explica en el informe qué más harías.

## Qué entregar

- Logs `lynis.log` y `report.dat` **antes y después** de cada máquina (en `evidencias/sistemas/`).
- En el informe: descripción de cada equipo, tabla de evolución del índice (inicial → final) y tabla de medidas aplicadas/descartadas con su motivo. Capturas del índice inicial y final.
