# PAI3-lab — PAI-3 VULNAWEB (Security Team 5)

Contexto del proyecto para Claude Code y para el equipo. Léelo al empezar cada sesión.

## Qué es

Práctica PAI-3 de Ingeniería de Seguridad (US). Hacemos de auditores de seguridad para una universidad ficticia (U-Secure) y entregamos un zip **`PAI3-ST5.zip`** con un informe PDF (máx. 15 páginas) y las evidencias.

**Deadline: 10 de noviembre 2026, 23:59.** Seguimiento el 3-4 nov. Entrega SOLO por la actividad de la Enseñanza Virtual (email o mensaje interno = -10%). Cada día de retraso = -10%.

Guía general (conceptos y visión de conjunto): https://claude.ai/artifact/TvXHcMk1XAdgRSgcnh4nQo
Guía detallada de cada parte: el `README.md` de cada carpeta (`sistemas/`, `navegador/`, `movil/`, `web/`).

## Las 4 auditorías

| # | Parte | Herramienta | Objetivo |
|---|-------|-------------|----------|
| 1 | Sistemas informáticos | **Lynis** | 2-3 equipos Linux con **hardening index ≥ 70**, cada medida justificada |
| 2 | Navegador web | Políticas corporativas (Firefox) | Directivas de hardening aplicadas y verificadas en `about:policies` |
| 3 | Sistema móvil | Malwarebytes **o** Koodous + ADB | **≥ 2 móviles** auditados y bastionados según checklist de la política |
| 4 | Sistema web | **OWASP ZAP** | Trazabilidad HTTP/HTTPS + **≥ 3 vulns OWASP Top 10** + plan de mitigación |

Estándares a citar en el informe: OWASP Top 10, CIS Benchmarks, NIST SP 800-115, ENS (categoría Alta).

## Reparto (somos 3)

| Persona | Partes | Por qué |
|---------|--------|---------|
| **Persona 1** | Parte 1 (Lynis) + Parte 2 (Navegador) | Las dos corren en la misma máquina Linux; la 2 es corta |
| **Persona 2** | Parte 3 (Móvil) + **consolidar el PDF** | El móvil es la parte más ligera, le queda tiempo para montar el informe |
| **Persona 3** | Parte 4 (Web / ZAP) | Es la parte más larga, va entera a una persona |

Cada uno escribe su sección del informe; Persona 2 junta todo y exporta el PDF.

## Reglas de oro

- **Solo entornos propios o de pruebas.** ZAP/fuzzers nunca contra webs reales. Atacar sin autorización es delito.
- **Todo se documenta.** El informe exige justificar cada cambio (y por qué se descartan otros).
- **Logs obligatorios** de TODAS las herramientas (Lynis, ZAP, móvil). Sin log, la parte no está demostrada.
- Cada log va a `evidencias/<parte>/` con fecha en el nombre: `lynis-ubuntu-antes-2026-11-02.log`.
- En VMs: hacer **snapshot** antes de bastionar.
- **Lo más simple que cumpla el enunciado.** No añadir herramientas ni pasos que el enunciado no pide.

## Estructura del repo

```
sistemas/    Parte 1 — guía + scripts Lynis + perfil custom.prf
navegador/   Parte 2 — guía + policies.json + script de despliegue
movil/       Parte 3 — guía + script de auditoría ADB + checklist
web/         Parte 4 — guía + payloads + notas ZAP
evidencias/  Logs y capturas (antes/después) de cada parte
informe/     Borrador del informe final (plantilla)
```

El zip de entrega es este repo comprimido + el PDF del informe, renombrado a `PAI3-ST5.zip`.

## Estado del código

Los scripts son **esqueletos comentados**: documentan QUÉ comando ejecutar y PARA QUÉ. Se rellenan cuando el equipo decida las máquinas/medidas concretas. No generar el código entero sin acordar antes el entorno.
