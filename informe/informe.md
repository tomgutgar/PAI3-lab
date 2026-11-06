# PAI-3 VULNAWEB — Informe (borrador)

> Plantilla con la estructura OBLIGATORIA del enunciado. Máx. 15 páginas (referencias y anexos NO cuentan).
> Se escribe aquí y se exporta a PDF (`informe_PAI3-ST<Num>.pdf`) para el zip.

## Portada

PAI-3 VULNAWEB · Security Team Nº ___ · Integrantes: ___ · Fecha: ___

## Índice

(automático al exportar)

## Resumen ejecutivo

_Media página. Una frase de resultado por parte._

- Sistemas: con `hardening.sh`, el hardening index de Lynis sube de 64 a 73 en Ubuntu y de 64 a 71 en Debian, ambos por encima del 70 exigido; la mejora viene sobre todo de añadir detección y auditoría (rkhunter, fail2ban, AIDE, auditd). _(Fedora pendiente.)_
- Web (Miguel): de los 6 endpoints de escritura probados, 5 aceptan peticiones sin ninguna autenticación, y el sexto usa un secreto JWT hardcodeado que se recupera en segundos con un diccionario dirigido.

## 1. Auditoría de sistemas informáticos

### 1.1 Descripción del sistema analizado y herramientas

Se han auditado **3 máquinas virtuales**, cada una con una distribución Linux distinta instalada desde su ISO oficial en su última versión estable: **Ubuntu 24.04.5 LTS** (última LTS), **Fedora** y **Debian 13**. Usar tres distribuciones permite comprobar que las medidas de bastionado son portables y no dependen de una distribución concreta. Antes de bastionar se tomó un *snapshot* de cada VM.

La auditoría se hace con **Lynis** (perfil por defecto), que revisa cientos de controles y devuelve un *hardening index* de 0 a 100. Se ejecuta antes y después del bastionado para medir la mejora. El bastionado se aplica con el script propio **`sistemas/hardening.sh`**, idempotente y organizado por grupos que corresponden a avisos concretos de Lynis (en Fedora, mismas medidas usando `dnf` en lugar de `apt`).

#### Herramientas y medidas que aplica `hardening.sh`

| Grupo | Herramienta / cambio | Cómo protege | Test de Lynis |
|-------|----------------------|--------------|---------------|
| `firewall` | **UFW**: deniega todo lo entrante, permite lo saliente | Cierra los puertos no usados; reduce la superficie de ataque por red | FIRE-4590 |
| `passwords` | **libpam-pwquality** (mín. 12 caracteres, con dígito y mayúscula), caducidad 90 días y `UMASK 027` en `login.defs` | Contraseñas resistentes a fuerza bruta y archivos nuevos no legibles por otros usuarios | AUTH-9262, AUTH-9286, AUTH-9328 |
| `banner` | Aviso legal en `/etc/issue` e `/issue.net` | Advierte de acceso restringido y registro de actividad (valor legal/disuasorio) | BANN-7126, BANN-7130 |
| `usb` | Bloqueo de los módulos `usb-storage` y `firewire` | Impide sacar datos o meter malware con memorias USB | STRG-1840, STRG-1846 |
| `kernel` | **sysctl** (`sysctl-hardening.conf`): anti-spoofing, sin redirecciones ICMP, SYN cookies, ASLR completo, ocultar punteros y `dmesg` | Protege la pila de red (spoofing, SYN flood, MITM) y dificulta explotar el kernel | KRNL-6000 |
| `coredumps` | `* hard core 0` en `limits.conf` | Evita volcados de memoria que podrían contener contraseñas o claves | KRNL-5820 |
| `herramientas` | **auditd** y **acct** (auditoría y registro de comandos), **sysstat** (estadísticas), **rkhunter** (detección de rootkits), **fail2ban** (bloquea IPs tras intentos fallidos), **AIDE** (integridad de ficheros), **apt-show-versions** (control de parches) | Añade detección y trazabilidad: si hay un ataque, se detecta y queda registrado | ACCT-*, HRDN-7230, FINT-4350, DEB-0880, PKGS-7394 |

**Por qué sube el índice de Lynis:** el *hardening index* se calcula con los controles que superan la comprobación frente al total evaluado. Cada grupo del script resuelve una o varias sugerencias concretas del informe inicial de Lynis (columna derecha), así que cada control corregido suma puntos. Se aplicó por grupos, repitiendo Lynis entre ellos, para ver qué aporta cada medida (capturas en `evidencias/sistemas/`).

### 1.2 Plan de pruebas y resultados

**Equipos.** `Pai-ubuntu` (Ubuntu 24.04.5 LTS) y `pai-debian` (Debian 13), ambos auditados con Lynis 3.1.8 el 2-nov-2026. _(Fedora: pendiente.)_

**Procedimiento** (en cada VM, siguiendo el esquema de NIST SP 800-115: auditar, corregir, volver a auditar):

1. `sudo ./run_lynis.sh antes`: auditoría inicial.
2. `sudo ./hardening.sh firewall` y nueva pasada de Lynis, para medir esta medida por separado. Esta pasada se guardó también con la etiqueta `antes` y sobrescribió el log inicial, así que el índice inicial (64) queda demostrado con la captura `PrimerTest*.png` y el log `antes` corresponde al estado tras el firewall.
3. `sudo ./hardening.sh`: el resto de grupos.
4. `sudo ./run_lynis.sh despues`: auditoría final.

**Resultados:**

| Equipo | Índice inicial | Tras firewall | Índice final | Puntos Lynis (tras firewall → final) | Sugerencias (tras firewall → final) |
|--------|:-----------:|:-------------:|:--------------:|:------------------------------:|:-----------------------------:|
| Ubuntu 24.04.5 | 64 | 66 | **73** | 206/312 → 242/330 | 44 → 38 |
| Debian 13      | 64 | 65 | **71** | 214/327 → 246/342 | 49 → 42 |

Los dos equipos superan el objetivo de **≥ 70**. Lynis ejecuta algunos tests más en la segunda pasada (270 → 282 en Ubuntu, 279 → 288 en Debian), porque al instalar herramientas nuevas, como AIDE o auditd, aparecen comprobaciones nuevas sobre ellas.

**Firewall (64 → 66 en Ubuntu, 64 → 65 en Debian).** Con UFW activo y la política "denegar todo lo entrante" (la que recomienda el CIS Benchmark), Lynis pasa a dar el firewall por configurado y el índice sube 1-2 puntos.

Evidencias: `evidencias/sistemas/Ubuntu/` y `evidencias/sistemas/Debian/`, con los logs y `report.dat` de Lynis y capturas de las tres pasadas: `PrimerTest*.png` (inicial), `SegundoTestFirewall*.png` (tras el firewall) y `TercerTestHardeningCompleto*.png` (final).

### 1.3 Conclusiones

Con un único script, idempotente y aplicable a ambas distribuciones, las dos máquinas pasan de un índice de 64 a **71-73**, por encima del 70 exigido. El firewall aporta 1-2 puntos; la mayor mejora (6-7 puntos) viene de las **herramientas de detección y auditoría** (rkhunter, fail2ban, AIDE, auditd, acct). Es decir, a las instalaciones por defecto de Ubuntu y Debian les falta sobre todo detectar y registrar lo que ocurre en el sistema.

## 2. Análisis y bastionado de navegador web

### 2.1 Descripción del sistema analizado
### 2.2 Plan de pruebas y resultados
### 2.3 Conclusiones

## 3. Auditoría de sistema móvil

### 3.1 Descripción del sistema analizado y herramientas
### 3.2 Plan de pruebas y resultados
### 3.3 Conclusiones

## 4. Auditoría de sistema web

### 4.1 Descripción del sistema web y herramientas

El objetivo es SOS-hardened, un fork propio del proyecto SOS2526-11 (asignatura SOS, curso anterior), con el mismo autor como uno de los tres contribuidores originales. Se audita en local, nunca contra la URL real que el equipo de SOS tiene desplegada en Render, por tratarse de un servicio compartido con terceros ajenos a esta práctica.

La guía de la asignatura propone DVWA como objetivo. Se usa SOS-hardened en su lugar porque cumple igual la norma de "solo entornos propios o de pruebas" y porque una revisión inicial del código ya mostraba fallos reales, sin necesidad de un laboratorio construido a propósito.

Stack: backend Node.js/Express con base de datos NeDB (ficheros planos) y autenticación JWT; frontend SvelteKit. Herramientas: OWASP ZAP 2.17 como proxy de interceptación y para las pruebas manuales (Spider, Requester), y `hashcat` (modo 16500, JWT) para comprobar la fortaleza del secreto de firma.

### 4.2 Plan de pruebas y resultados

**Trazabilidad del tráfico.** Con el navegador configurado para pasar por el proxy de ZAP (puerto 8082) se navegó por la aplicación sin modificar ninguna petición. La pestaña History de ZAP registra cada petición y respuesta, incluida la del login, con sus cabeceras y su cuerpo — queda demostrado que todo el tráfico HTTP pasa por el proxy sin alterarse. No se importó el certificado raíz de ZAP porque la aplicación sirve por HTTP, no HTTPS; ese paso solo es necesario para interceptar tráfico cifrado.

**Metodología seguida**, en caja negra: reconocimiento con el Spider de ZAP para mapear las rutas de la aplicación (incluida la API, versionada en `v1` y `v2`, con tres recursos cada una); prueba de autenticación en cada endpoint de escritura, sin ninguna cabecera; localización del endpoint real de login observando el tráfico generado al enviar el formulario; y, una vez obtenido un token, análisis de su cabecera y crackeo del secreto de firma con una wordlist construida a partir de los nombres del equipo visibles en la propia web.

**Vulnerabilidad 1 — Control de acceso roto (A01:2021).** Se probó `DELETE` sin autenticación contra los 6 endpoints de recurso de la API (3 recursos × 2 versiones):

| Recurso | v1 | v2 |
|---|---|---|
| alcohol-consumptions-per-capita | sin protección | protegido |
| literacy-rates | sin protección | sin protección |
| road-fatalities | sin protección | sin protección |

5 de 6 aceptan el borrado completo de la colección sin pedir ningún tipo de credencial.

**Vulnerabilidad 2 — Secreto de firma JWT débil y recuperable (A02:2021).** El único endpoint protegido (alcohol v2) usa un token JWT firmado con HS256. Tras obtener un token válido, se guardó y se atacó offline con `hashcat`: el diccionario genérico (`rockyou.txt`) no lo recupera, pero una wordlist de 360 combinaciones (palabras típicas de contraseña + nombres del equipo, sacados de la propia página de inicio) lo crackea en menos de un segundo. Con el secreto en mano se puede firmar un token válido para cualquier usuario sin pasar por el login. Aparte, el secreto sigue recuperable en el historial de git aunque se rote en el código actual (repo público); rotarlo en el HEAD no deshace la exposición pasada, por eso se trata como comprometido para siempre y no se intenta "arreglar" reescribiendo el historial.

**Vulnerabilidad 3 — Credenciales por defecto (A07:2021).** El login de ese mismo endpoint acepta `admin`/`admin`.

**Vulnerabilidad 4 — Inyección NoSQL (A03:2021), adicional.** Los filtros de los `GET` de la API pasan los parámetros de la query string directamente a la base de datos sin comprobar su tipo. Fuzzing con ZAP sobre el parámetro `nation` con 5 operadores de NeDB (`$ne`, `$gt`, `$regex`, `$exists`, `$where`) muestra que los 5 se saltan el filtro por igual: la petición de control devuelve 342 bytes (3 resultados), y las 5 inyectadas devuelven 17.148 bytes, el tamaño exacto de la colección completa. El impacto en este endpoint concreto es bajo, porque es público y sin filtro ya devuelve todo; el riesgo real es que el mismo patrón de código, sin saneamiento de tipos, se repite en otros puntos de la aplicación, y que el operador `$where` podría usarse para ejecutar código si se le pasara una función en vez del valor simple usado en la prueba.

**Dependencias desactualizadas (A06:2021), adicional.** `npm audit` reporta 35 vulnerabilidades (11 moderate, 19 high, 5 critical). La más relevante es `nedb`, la propia base de datos de la aplicación en producción: tiene una vulnerabilidad crítica de Prototype Pollution sin parche disponible. El resto de las críticas y altas vienen de dependencias de testing (`newman`, `postman-*`), no de producción.

Evidencia (peticiones, respuestas, resultados de hashcat y log de `npm audit`) en `evidencias/web/capturas/` y `evidencias/web/npm-audit-2026-11-06.log`; informe HTML generado por ZAP en `evidencias/web/2026-11-06-ZAP-Report-localhost.html` y exportación del tráfico capturado en `evidencias/web/zap-history-export.csv`; notas detalladas en `evidencias/web/notas-sesion.md`.

### 4.3 Plan de mitigación y demostración (antes/después)

Se corrigieron las 4 vulnerabilidades en el código de `SOS-hardened`: un middleware de autenticación (`verifyToken`) centralizado y aplicado a todos los endpoints de escritura de los 6 ficheros de la API (antes solo protegía uno de seis); el secreto de firma JWT y las credenciales de login movidos a variables de entorno, generadas aleatoriamente, fuera del código fuente y del repositorio; y un saneador (`stringFilter`) que descarta cualquier valor de filtro que no sea un string plano, bloqueando la inyección de operadores NoSQL.

Repitiendo exactamente los mismos ataques de la sección 4.2:

| Vulnerabilidad | Antes | Después |
|---|---|---|
| Acceso sin autenticación | 5/6 endpoints en `200 OK` sin credenciales | 6/6 en `403 Forbidden` |
| Secreto JWT filtrado | Token forjado con el secreto expuesto, aceptado | Rechazado (`401`); secreto rotado y fuera del código |
| Credenciales hardcodeadas | `admin`/`admin` funcionaba | Rechazado (`401`); credenciales aleatorias en `.env` |
| Inyección NoSQL | El operador `$ne` alteraba el resultado de la consulta | El operador se descarta antes de llegar a la base de datos (verificado comparando `nation[$ne]=Spain` contra la consulta sin filtro: ambas devuelven el mismo número de resultados, 150, cuando una inyección real habría dado 147) |

Se comprobó también que la funcionalidad legítima sigue intacta: el login con las credenciales nuevas devuelve un token válido, y ese token permite realizar un `PUT` real sobre un recurso.

### 4.4 Conclusiones

El sistema no tenía, en la práctica, control de acceso: la autenticación faltaba en la mayoría de los endpoints de escritura, y donde existía dependía de un secreto adivinable con un diccionario pequeño y de credenciales por defecto nunca cambiadas. Eran fallos de diseño, no detalles sueltos — por eso la corrección no se limitó a parchear un endpoint, sino a centralizar la autenticación y el saneamiento de entrada de forma uniforme en toda la API. Queda como deuda técnica no resuelta en esta práctica la actualización de dependencias (`npm audit`), en particular `nedb`, que no tiene parche disponible para su vulnerabilidad crítica.

## Referencias

_(no cuentan para las 15 páginas)_

## Anexos

_(logs largos y capturas extra; no cuentan para las 15 páginas)_
