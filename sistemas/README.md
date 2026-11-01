# Parte 1 — Auditoría de sistemas (Lynis)

Objetivo: 2-3 equipos Linux con hardening index ≥ 70, documentando cada medida.

## Flujo

1. VM Linux actualizada + snapshot.
2. `sudo ./run_lynis.sh antes` → escaneo inicial, copia logs a `../evidencias/sistemas/`.
3. Revisar sugerencias y warnings; decidir medidas (ver guía).
4. `sudo ./hardening.sh` por grupos, repitiendo `run_lynis.sh` para ver cuánto sube.
5. `sudo ./run_lynis.sh despues` → escaneo final.
6. Repetir en el resto de equipos.

## Ficheros de Lynis

- `/var/log/lynis.log` — detalle (se sobrescribe cada pasada → copiar).
- `/var/log/lynis-report.dat` — resumen clave=valor.
