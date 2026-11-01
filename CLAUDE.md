# py3lab — PAI-3 VULNAWEB

Contexto del proyecto para Claude Code y para el equipo. Léelo al empezar cada sesión.

## Qué es

Practica PAI-3 de Ingeniería de Seguridad (US). Hacemos de auditores de seguridad para una universidad ficticia (U-Secure) y entregamos un zip `PAI3-ST<Num>.zip` con un informe PDF (máx. 15 páginas) y las evidencias.

**Deadline: 10 de noviembre 2026, 23:59.** Seguimiento el 3-4 nov. Entrega SOLO por la actividad de la Enseñanza Virtual (email o mensaje interno = -10%). Cada día de retraso = -10%.

Guía completa para el equipo (documento vivo): https://claude.ai/artifact/TvXHcMk1XAdgRSgcnh4nQo

## Las 4 auditorías

| # | Parte | Herramienta | Objetivo |
|---|-------|-------------|----------|
| 1 | Sistemas informáticos | **Lynis** | 2-3 equipos Linux con **hardening index ≥ 70**, cada medida justificada |
| 2 | Navegador web | Políticas corporativas (Firefox/Chromium/Brave) | Directivas de hardening aplicadas y verificadas en `about:policies` |
| 3 | Sistema móvil | MobSF / Koodous / Malwarebytes + ADB | **≥ 2 móviles** auditados y bastionados según checklist de la política |
| 4 | Sistema web | **OWASP ZAP** | Trazabilidad HTTP/HTTPS + **≥ 3 vulns OWASP Top 10** + plan de mitigación |

Estándares de referencia a citar: OWASP Top 10, CIS Benchmarks, NIST SP 800-115, ENS (categoría Alta).

## Reglas de oro

- **Solo entornos propios o de pruebas.** ZAP/fuzzers nunca contra webs reales. Atacar sin autorización es delito.
- **Todo se documenta.** El informe exige justificar cada cambio (y por qué se descartan otros).
- **Logs obligatorios** de TODAS las herramientas (Lynis, ZAP, móvil). Sin log, la parte no está demostrada.
- Cada log va a `evidencias/<parte>/` con fecha en el nombre: `lynis-ubuntu-antes-2026-11-02.log`.
- En VMs: hacer **snapshot** antes de bastionar.

## Estructura del repo

```
sistemas/    Parte 1 — scripts Lynis + perfil custom.prf
navegador/   Parte 2 — policies.json + script de despliegue
movil/       Parte 3 — script de auditoría ADB
web/         Parte 4 — docker DVWA + payloads + notas ZAP
evidencias/  Logs y capturas (antes/después) de cada parte
informe/     Borrador del informe final (plantilla)
```

El zip de entrega es este repo comprimido + el PDF del informe. Renombrar a `PAI3-ST<Num>.zip`.

## Estado del código

Los scripts son **esqueletos comentados**: documentan QUÉ comando ejecutar y PARA QUÉ. Falta rellenar la implementación cuando el equipo decida las máquinas/medidas concretas. No generar el código entero sin acordar antes el entorno.

## Equipo

- Security Team Nº: **PENDIENTE** (rellenar y poner en el nombre del zip).
- Reparto sugerido: 1 persona por parte; el informe lo edita una sola persona para evitar conflictos.
