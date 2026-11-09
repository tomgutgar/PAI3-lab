# Parte 3 — Auditoría de móvil · Persona 2

> Objetivo: analizar **al menos 2 móviles Android** (los vuestros valen) con **una** herramienta de seguridad, comprobar los 8 puntos de la política, corregir lo que falle y demostrarlo con capturas y logs.

## Qué necesitas saber

- **BYOD**: el móvil es personal pero se usa para servicios de la universidad. Si está comprometido, la universidad también.
- **Root**: tener superusuario en el móvil; rompe el aislamiento entre apps. Hay que comprobar que NO lo tiene.
- **Sideloading**: instalar apps fuera de Google Play; es la vía principal de malware.
- **ADB** (Android Debug Bridge): programa de Google para dar órdenes al móvil desde el PC por USB. Lo usamos para sacar los **logs en texto** que hay que entregar.

## Herramientas

- **Una** app de análisis en el móvil: **Malwarebytes** o **Koodous** (elige una). Es la herramienta principal que pide el enunciado.
- **ADB** en el PC para los logs. Se instala con las *platform-tools* de Google: https://developer.android.com/tools/releases/platform-tools
- Para el punto B2, `conexiones_b2.sh` lista por ADB las conexiones abiertas y la app que tiene cada una (con Chrome en uso).

## Paso a paso

1. En el móvil: Ajustes → acerca del teléfono → tocar 7 veces "Número de compilación" (activa Opciones de desarrollador) → activar **Depuración USB**.
2. Conecta al PC y ejecuta `adb devices` (acepta la huella en el móvil).
3. **Antes**: `./auditar_android.sh <modelo> antes` (vuelca el estado a `evidencias/movil/<modelo>-antes/`) y escanea con Malwarebytes/Koodous (capturas).
4. Rellena `checklist.md` (qué cumple y qué no).
5. **Corrige** lo que falle (columna "corrección" de la checklist).
6. **Después**: `./auditar_android.sh <modelo> despues` + nuevo escaneo.
7. Al terminar, **desactiva la Depuración USB** (también es bastionado).
8. Repite con el segundo móvil.

## Checklist de la política (está en `checklist.md`)

| # | Medida | Cómo comprobar (ADB) |
|---|--------|----------------------|
| A1 | Orígenes desconocidos off | Ajustes → instalar apps desconocidas |
| A2 | Sin root | `adb shell which su` (vacío), `getprop ro.boot.verifiedbootstate` = green |
| A3 | Parche al día | `getprop ro.build.version.security_patch` |
| A4 | Sin Wi-Fi inseguras | `adb shell cmd wifi list-networks` |
| A5 | Bluetooth apagado | `adb shell settings get global bluetooth_on` |
| B1 | Sin malware | escaneo + `adb shell pm list packages -3 -i` |
| B2 | Sin conexiones de fondo raras | `conexiones_b2.sh` con Chrome abierto |
| B3 | Sin permisos peligrosos | `settings get secure enabled_accessibility_services`, overlay, almacenamiento |

## Qué entregar

- Carpeta por móvil con los logs del script antes/después y las capturas del escaneo.
- `checklist.md` rellena (antes/después).
- En el informe: modelo y versión de Android de cada móvil, la checklist y las correcciones aplicadas.
