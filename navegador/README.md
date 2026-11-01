# Parte 2 — Bastionado del navegador · Persona 1

> Objetivo: definir unas **directivas corporativas** para el navegador de una de tus máquinas Linux (la misma de la Parte 1), aplicarlas con un **fichero de políticas** (no a mano en los ajustes) y demostrar que funcionan. Cada directiva va justificada en el informe.

## Qué necesitas saber

- El navegador es la puerta a los servicios de la universidad: si está mal configurado, es un vector de ataque (extensiones maliciosas, contraseñas guardadas, HTTPS desactivado...).
- Una **política corporativa** es un fichero JSON que el navegador lee al arrancar y que el usuario normal no puede cambiar. Es como lo hacen las empresas, y es lo que pide el enunciado.
- Usa **Firefox** (viene en Ubuntu y sus políticas están muy documentadas). Fichero: `/etc/firefox/policies/policies.json`. Se comprueba en `about:policies`.

## Paso a paso

1. **Antes**: con Firefox sin tocar, pasa las pruebas de la tabla de abajo y haz capturas.
2. Edita `firefox/policies.json` con las directivas (ya tiene un esqueleto). Apunta la justificación de cada una en `directivas.md`.
3. Despliega: `sudo ./desplegar.sh firefox`.
4. Reinicia Firefox y abre `about:policies`: deben aparecer. **Captura** (es la prueba de que están aplicadas).
5. **Después**: repite las pruebas. Tabla antes/después.

## Directivas recomendadas (Firefox)

| Riesgo | Directiva |
|--------|-----------|
| Tráfico sin cifrar | `HttpsOnlyMode: force_enabled` |
| TLS viejo | `SSLVersionMin: tls1.2` |
| Rastreo | `EnableTrackingProtection` (Cryptomining, Fingerprinting) |
| Contraseñas en el navegador | `PasswordManagerEnabled: false`, `OfferToSaveLogins: false` |
| Extensiones maliciosas | `ExtensionSettings`: bloquear `*` + lista blanca |
| Telemetría | `DisableTelemetry`, `DisableFirefoxStudies` |
| Usuario saltándose la política | `BlockAboutConfig: true` |

Referencia completa: https://mozilla.github.io/policy-templates/

## Plan de pruebas (antes/después)

| Prueba | Web | Esperado tras bastionar |
|--------|-----|-------------------------|
| Certificados malos / TLS viejo | https://badssl.com | Bloquea las conexiones inseguras |
| HTTP sin cifrar | http://http.badssl.com | Aviso de HTTPS-Only |
| Extensiones | Intentar instalar una fuera de la lista | Bloqueada por la política |
| Contraseñas | Login en cualquier web | No ofrece guardar la contraseña |

## Qué entregar

- `policies.json` y `directivas.md`.
- Capturas de `about:policies` y de las pruebas antes/después (en `evidencias/navegador/`).
- En el informe: descripción del navegador, tabla de directivas con su justificación y resultados de las pruebas.
