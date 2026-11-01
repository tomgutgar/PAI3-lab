# Parte 3 — Auditoría de móvil

Objetivo: ≥ 2 móviles Android auditados y bastionados según la checklist de la política.

## Flujo

1. Activar Opciones de desarrollador + Depuración USB. `adb devices` para confirmar.
2. `./auditar_android.sh <modelo> antes` → vuelca estado a `../evidencias/movil/<modelo>-antes/`.
3. Escaneo con Malwarebytes o Koodous (capturas).
4. PCAPdroid: usar el navegador unos minutos, exportar conexiones.
5. Repasar `checklist.md`, corregir, y `./auditar_android.sh <modelo> despues`.
6. Al terminar: **desactivar Depuración USB** (también es bastionado).

Herramientas: Malwarebytes/Koodous (en el móvil), ADB (PC), PCAPdroid (sin root), MobSF (opcional, Docker, para analizar una APK).
