# Checklist de la política (antes/después por móvil)

## Móvil 1

Modelo: Google Pixel 9 Pro    Android: 17 (parche 2026-10-05)    Herramienta de escaneo: Malwarebytes

| # | Medida | Cumple antes | Cumple después | Corrección aplicada |
|---|--------|:---:|:---:|------------|
| A1 | Orígenes desconocidos desactivados | Sí | Sí | — |
| A2 | Sin root ni kernel modificado | Sí | Sí | — |
| A3 | Sistema y navegador al día | Sí | Sí | — (sistema sin actualizaciones pendientes y Chrome al día en Play Store) |
| A4 | Sin Wi-Fi abiertas / WEP / WPA-basic | Sí | Sí | — |
| A5 | Bluetooth apagado en sesión corporativa | No | Sí | Bluetooth apagado desde ajustes rápidos |
| B1 | Sin malware ni APKs sospechosas | Sí | Sí | — |
| B2 | Sin conexiones de fondo no autorizadas | No | Sí | Con Chrome en uso, `com.chess`, `com.anthropic.claude` y YouTube tenían conexiones abiertas en segundo plano: forzada su detención (`conexiones_b2.sh`) |
| B3 | Sin permisos peligrosos a terceros | Sí | Sí | — |

## Móvil 2

Modelo: Google Pixel 10    Android: 17 (parche 2026-10-05)    Herramienta de escaneo: Malwarebytes

| # | Medida | Cumple antes | Cumple después | Corrección aplicada |
|---|--------|:---:|:---:|------------|
| A1 | Orígenes desconocidos desactivados | Sí | Sí | — |
| A2 | Sin root ni kernel modificado | Sí | Sí | — |
| A3 | Sistema y navegador al día | No | Sí | Sistema al día (parche 2026-10-05, sin actualizaciones pendientes), pero Chrome tenía una actualización pendiente en Play Store: actualizado desde Play Store |
| A4 | Sin Wi-Fi abiertas / WEP / WPA-basic | No | Sí | Se olvidaron 6 redes guardadas sin cifrado (Andared_IoT, Carrefour-Conecta, QUIRONSALUD, Quironsalud_Invitados, VuelingWi-Fi y la variante abierta de paradores); además se olvidaron 2 redes con SSID oculto sin Enterprise (Livebox7-789E-WiFi7 y alternative-wifi-etsi) |
| A5 | Bluetooth apagado en sesión corporativa | Sí | Sí | — |
| B1 | Sin malware ni APKs sospechosas | Sí | Sí | — |
| B2 | Sin conexiones de fondo no autorizadas | No | Sí | Con Chrome en uso, `es.larazon`, `com.iphonedroid.marca` y Google TV tenían conexiones abiertas en segundo plano: forzada su detención (`conexiones_b2.sh`) |
| B3 | Sin permisos peligrosos a terceros | No | Sí | Retirado con `pm revoke` el permiso de leer el almacenamiento compartido a 6 apps de terceros (explorador de archivos, Adobe Reader, WhatsApp, Dropbox, Telegram y Séneca) |
