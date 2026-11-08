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
- Web: de los 6 endpoints de escritura probados, 5 aceptan peticiones sin ninguna autenticación, y el sexto usa un secreto JWT hardcodeado que se recupera en segundos con un diccionario dirigido.
- Móvil: los 2 Pixel auditados no tenían root ni malware, pero fallaban en puntos de higiene de la política (Bluetooth encendido en uno; Chrome sin actualizar y Wi-Fi abiertas guardadas en el otro), corregidos y verificados después.

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

Se auditaron **2 móviles Android** personales (BYOD), ambos Google Pixel: un **Pixel 9 Pro** y un **Pixel 10**, los dos con Android 17 y parche de seguridad del 05-10-2026. Se comprobaron 7 de los 8 puntos de la política (A1-A5, B1 y B3; el B2 es opcional y no se comprobó) mediante **ADB** (Android Debug Bridge), con un script propio (`movil/auditar_android.sh`) que vuelca por consola el estado de cada punto comprobable, y **Malwarebytes** como herramienta de escaneo antimalware, instalada en cada móvil para el punto B1.

### 3.2 Plan de pruebas y resultados

**Procedimiento** en cada móvil: activar Opciones de desarrollador y Depuración USB, volcado `antes` con el script, escaneo con Malwarebytes, corrección de lo que falle, volcado `despues`, y desactivar la Depuración USB al terminar. El escaneo de Malwarebytes se hizo una vez por móvil, antes de corregir, porque las correcciones (Bluetooth, redes Wi-Fi y Chrome) no instalan ni quitan aplicaciones y no cambian el resultado de B1.

**Resultados** (detalle completo en `movil/checklist.md`):

| Punto | Pixel 9 Pro | Pixel 10 |
|---|:---:|:---:|
| A1. Orígenes desconocidos desactivados | Cumple | Cumple |
| A2. Sin root | Cumple | Cumple |
| A3. Sistema y navegador al día | Cumple | **No cumplía** (Chrome) |
| A4. Sin Wi-Fi inseguras | Cumple | **No cumplía** |
| A5. Bluetooth apagado | **No cumplía** | Cumple |
| B1. Sin malware | Cumple | Cumple |
| B2. Sin conexiones de fondo no autorizadas | No comprobado (opcional) | No comprobado (opcional) |
| B3. Sin permisos peligrosos | Cumple | Cumple |

El punto A1 se comprobó a mano en cada móvil (Ajustes → Instalar aplicaciones desconocidas: ninguna app con el permiso concedido) y el A3 en Ajustes → Actualizaciones de software y en la ficha de Chrome en Play Store, porque el script solo da el nivel de parche.

En el Pixel 9 Pro el único fallo fue el Bluetooth encendido, corregido apagándolo. En el Pixel 10 hubo dos. El primero, A3: el sistema estaba al día, pero Chrome tenía una actualización pendiente en Play Store, y se corrigió actualizándolo (la ficha pasa de "Actualizar" a "Abrir"). El segundo, A4: tenía 6 redes Wi-Fi guardadas sin cifrado (`Andared_IoT`, `Carrefour-Conecta`, `QUIRONSALUD`, `Quironsalud_Invitados`, `VuelingWi-Fi` y una variante abierta de `paradores`), típicas de wifis públicas de aeropuertos, hospitales o comercios; se corrigió olvidando esas 6 redes, verificado con `adb shell cmd wifi list-networks` antes y después. El punto B2 (conexiones de fondo) es opcional según el README de esta parte y no se comprobó, al no usarse PCAPdroid.

Evidencia: logs de ADB en `evidencias/movil/<modelo>-antes/` y `evidencias/movil/<modelo>-despues/`; capturas del escaneo de Malwarebytes, del permiso de instalar apps desconocidas (A1) y de las actualizaciones de sistema y de Chrome (A3) en las carpetas `-antes`.

![Pixel 10: Chrome con actualización pendiente en Play Store (A3)](../evidencias/movil/pixel10-antes/a3-chrome-desactualizado.png)

![Escaneo de Malwarebytes en el Pixel 9 Pro, sin amenazas](../evidencias/movil/pixel9pro-antes/malwarebytes-scan.png)

![Escaneo de Malwarebytes en el Pixel 10, sin amenazas](../evidencias/movil/pixel10-antes/malwarebytes-scan.png)

### 3.3 Conclusiones

Los dos móviles partían de un nivel de seguridad razonable, sin root, sin apps de origen desconocido y sin malware, pero los dos tenían fallos de higiene: el Pixel 9 Pro con el Bluetooth encendido sin necesidad, y el Pixel 10 con el navegador sin actualizar y arrastrando redes Wi-Fi abiertas de sitios públicos. Ninguno es grave por sí solo, pero todos amplían la superficie de ataque: con el Bluetooth activo hay más vías de conexión no solicitada, un navegador desactualizado puede tener vulnerabilidades ya públicas, y una red abierta guardada permite que el móvil se reconecte solo a una red que puede estar controlada por un atacante. Son fallos que se acumulan con el uso diario sin que el usuario lo note, así que conviene revisarlos de forma periódica y no solo una vez.

## 4. Auditoría de sistema web

### 4.1 Descripción del sistema web y herramientas

El objetivo es SOS-hardened, un fork propio del proyecto SOS2526-11 (asignatura SOS, curso anterior), con el mismo autor como uno de los tres contribuidores originales. Se audita en local, nunca contra la URL real que el equipo de SOS tiene desplegada en Render, por tratarse de un servicio compartido con terceros ajenos a esta práctica.

La guía de la asignatura propone DVWA como objetivo. Se usa SOS-hardened en su lugar porque cumple igual la norma de "solo entornos propios o de pruebas" y porque una revisión inicial del código ya mostraba fallos reales, sin necesidad de un laboratorio construido a propósito.

Stack: backend Node.js/Express con base de datos NeDB (ficheros planos) y autenticación JWT; frontend SvelteKit. Herramientas: OWASP ZAP 2.17 como proxy de interceptación y para las pruebas (Spider, Requester y Fuzzer), y `hashcat` (modo 16500, JWT) para comprobar la fortaleza del secreto de firma.

### 4.2 Plan de pruebas y resultados

**Trazabilidad del tráfico.** Con ZAP escuchando en `localhost:8082` y Firefox configurado a mano para usar ese proxy también en HTTPS (capturas `#5-zap-proxy-8082.png` y `#5-firefox-proxy-manual.png`) se navegó por la aplicación sin modificar ninguna petición. La pestaña History de ZAP registra cada petición y respuesta, incluida la del login, con sus cabeceras y su cuerpo, y queda demostrado así que todo el tráfico HTTP pasa por el proxy sin alterarse.

Para demostrar también la trazabilidad en HTTPS, se importó el certificado raíz de ZAP en Firefox (Autoridades → Importar → "Confiar en esta CA para identificar sitios web") y se navegó con el proxy activo a `https://example.com`, un dominio externo ajeno a esta práctica usado únicamente para comprobar la intercepción. El certificado de esa página, visto desde el propio navegador, tiene como emisor "Zed Attack Proxy Root CA" en vez del emisor real del sitio, lo que confirma que ZAP genera un certificado propio por cada dominio y que el tráfico cifrado pasa igual por el proxy; la petición `https://example.com/` con `200 OK` queda también registrada en la pestaña History. Capturas: `#5-cert-zap-importado.png` (CA de ZAP en Autoridades), `#5-cert-zap-emisor-https.png` (certificado con emisor ZAP) y `#5-zap-history-https.png` (petición HTTPS en History).

![Certificado de example.com emitido por Zed Attack Proxy Root CA](../evidencias/web/capturas/%235-cert-zap-emisor-https.png)

**Metodología seguida**, en caja negra: reconocimiento con el Spider de ZAP para mapear las rutas de la aplicación (incluida la API, versionada en `v1` y `v2`, con tres recursos cada una); prueba de autenticación en cada endpoint de escritura, sin ninguna cabecera; localización del endpoint real de login observando el tráfico generado al enviar el formulario; y, una vez obtenido un token, análisis de su cabecera y crackeo del secreto de firma con una wordlist construida a partir de los nombres del equipo visibles en la propia web.

**Vulnerabilidad 1. Control de acceso roto (A01:2021).** Se probó `DELETE` sin autenticación contra los 6 endpoints de recurso de la API (3 recursos × 2 versiones):

| Recurso | v1 | v2 |
|---|---|---|
| alcohol-consumptions-per-capita | sin protección | protegido |
| literacy-rates | sin protección | sin protección |
| road-fatalities | sin protección | sin protección |

5 de 6 aceptan el borrado completo de la colección sin pedir ningún tipo de credencial.

![DELETE sin autenticación aceptado](../evidencias/web/capturas/%231-acceso-sin-auth.png)

**Vulnerabilidad 2. Secreto de firma JWT débil y recuperable (A02:2021).** El único endpoint protegido (alcohol v2) usa un token JWT firmado con HS256. Tras obtener un token válido, se guardó y se atacó offline con `hashcat`: el diccionario genérico (`rockyou.txt`) no lo recupera, pero una wordlist de 360 combinaciones (palabras típicas de contraseña + nombres del equipo, sacados de la propia página de inicio) lo crackea en menos de un segundo. Con el secreto en mano se puede firmar un token válido para cualquier usuario sin pasar por el login. Aparte, el secreto sigue recuperable en el historial de git aunque se rote en el código actual (repo público); rotarlo en el HEAD no deshace la exposición pasada, por eso se trata como comprometido para siempre y no se intenta "arreglar" reescribiendo el historial.

![Secreto JWT crackeado con hashcat](../evidencias/web/capturas/%232-hashcat-wordlist-crackeado.png)

**Vulnerabilidad 3. Credenciales por defecto (A07:2021).** El login de ese mismo endpoint acepta `admin`/`admin`.

![Login con credenciales admin/admin](../evidencias/web/capturas/%233-login-response.png)

**Vulnerabilidad 4. Inyección NoSQL (A03:2021), adicional.** Los filtros de los `GET` de la API pasan los parámetros de la query string directamente a la base de datos sin comprobar su tipo. Fuzzing con ZAP sobre el parámetro `nation` con 5 operadores de NeDB (`$ne`, `$gt`, `$regex`, `$exists`, `$where`; lista en `web/payloads/nosql.txt` y captura `#4-fuzzer-payloads-nosql.png`) muestra que los 5 se saltan el filtro por igual: la petición de control devuelve 342 bytes (3 resultados), y las 5 inyectadas devuelven 17.148 bytes, el tamaño exacto de la colección completa. El impacto en este endpoint concreto es bajo, porque es público y sin filtro ya devuelve todo; el riesgo real es que el mismo patrón de código, sin saneamiento de tipos, se repite en otros puntos de la aplicación, y que el operador `$where` podría usarse para ejecutar código si se le pasara una función en vez del valor simple usado en la prueba.

![Fuzzer de ZAP con los 5 operadores NoSQL inyectados](../evidencias/web/capturas/%234-fuzzer-nosql-caja-negra.png)

**Dependencias desactualizadas (A06:2021), adicional.** `npm audit` reporta 35 vulnerabilidades (11 moderate, 19 high, 5 critical). La más relevante es `nedb`, la propia base de datos de la aplicación en producción: tiene una vulnerabilidad crítica de Prototype Pollution sin parche disponible. El resto de las críticas y altas vienen de dependencias de testing (`newman`, `postman-*`), no de producción.

**SQL Injection, XSS y Path Traversal (vectores que cita el enunciado).** Se probaron también estos tres vectores, aunque la aplicación no usa SQL (NeDB no es relacional, por lo que la inyección equivalente es la NoSQL ya descrita en la vulnerabilidad 4):

- *Path Traversal*: 8 variantes de escape de directorio (`../../..`, codificación simple y doble, `....//`) contra la carpeta estática y contra rutas de la API. Las 8 devuelven `404`. No vulnerable: SvelteKit sirve los estáticos con su propio manejador, sin exponer el sistema de ficheros, y las rutas de la API no toman ningún parámetro de ruta o nombre de fichero.
- *XSS reflejado*: el payload `<script>alert(1)</script>` en parámetros de consulta y en la URL no aparece en ninguna respuesta. No hay eco de parámetros en HTML, así que no es vulnerable por esta vía.
- *XSS almacenado*: un registro con `nation = "<img src=x onerror=alert(document.domain)>"` se guarda y se devuelve igual por la API: el valor es un string, así que pasa el control de tipo, pero nadie valida ni limpia su contenido. El frontend lo muestra en tablas con Svelte, que escapa el texto por defecto, y en gráficos con Highcharts, que filtra etiquetas y atributos peligrosos; no se llegó a confirmar la ejecución del script en el navegador, así que se reporta como entrada sin sanear y no como XSS confirmado. La prueba se hizo con un token válido sobre la versión ya corregida, por lo que este punto sigue abierto después de la mitigación (ver 4.4).

Evidencia de los tres en `evidencias/web/xss-path-traversal-2026-11-08.log`.

Evidencia (peticiones, respuestas, resultados de hashcat y log de `npm audit`) en `evidencias/web/capturas/` y `evidencias/web/npm-audit-2026-11-06.log`; informe HTML generado por ZAP en `evidencias/web/2026-11-06-ZAP-Report-localhost.html` y exportación del tráfico capturado en `evidencias/web/zap-history-export.csv`; notas detalladas en `evidencias/web/notas-sesion.md`.

### 4.3 Plan de mitigación y demostración (antes/después)

Se corrigieron las 4 vulnerabilidades en el código de `SOS-hardened`: un middleware de autenticación (`verifyToken`) centralizado y aplicado a todos los endpoints de escritura de los 6 ficheros de la API (antes solo protegía uno de seis); el secreto de firma JWT y las credenciales de login movidos a variables de entorno, generadas aleatoriamente, fuera del código fuente y del repositorio; y un saneador (`stringFilter`) que descarta cualquier valor de filtro que no sea un string plano, bloqueando la inyección de operadores NoSQL. El cambio completo está en `web/mitigacion-sos-hardened.patch` (9 ficheros, 118 líneas añadidas y 66 eliminadas) y publicado en https://github.com/Ridawo/SOS-hardened.

Repitiendo exactamente los mismos ataques de la sección 4.2:

| Vulnerabilidad | Antes | Después |
|---|---|---|
| Acceso sin autenticación | 5/6 endpoints en `200 OK` sin credenciales | 6/6 en `403 Forbidden` |
| Secreto JWT filtrado | Token forjado con el secreto expuesto, aceptado | Rechazado (`401`); secreto rotado y fuera del código |
| Credenciales hardcodeadas | `admin`/`admin` funcionaba | Rechazado (`401`); credenciales aleatorias en `.env` |
| Inyección NoSQL | El operador `$ne` alteraba el resultado de la consulta | El operador se descarta antes de llegar a la base de datos (verificado comparando `nation[$ne]=Spain` contra la consulta sin filtro: ambas devuelven el mismo número de resultados, 150, cuando una inyección real habría dado 147) |

Se comprobó también que la funcionalidad legítima sigue intacta: el login con las credenciales nuevas devuelve un token válido, y ese token permite realizar un `PUT` real sobre un recurso.

### 4.4 Conclusiones

El sistema no tenía, en la práctica, control de acceso: la autenticación faltaba en la mayoría de los endpoints de escritura, y donde existía dependía de un secreto adivinable con un diccionario pequeño y de credenciales por defecto nunca cambiadas. Eran fallos de diseño, no detalles sueltos, así que la corrección no se limitó a parchear un endpoint, sino a centralizar la autenticación y el saneamiento de entrada de forma uniforme en toda la API. Quedan como deuda técnica no resuelta en esta práctica la actualización de dependencias (`npm audit`), en particular `nedb`, que no tiene parche disponible para su vulnerabilidad crítica, y la validación del contenido de los campos de texto en los `POST`/`PUT`, que hoy aceptan HTML y solo están protegidos por el escapado del frontend.

## Referencias

_(no cuentan para las 15 páginas)_

- OWASP. *OWASP Top 10:2021*. https://owasp.org/Top10/
- CIS (Center for Internet Security). *CIS Benchmarks*. https://www.cisecurity.org/cis-benchmarks
- NIST. *SP 800-115: Technical Guide to Information Security Testing and Assessment*. https://csrc.nist.gov/pubs/sp/800/115/final
- España. Real Decreto 311/2022, de 3 de mayo, por el que se regula el Esquema Nacional de Seguridad (ENS), categoría Alta. CCN-CERT. https://www.ccn-cert.cni.es/
- CISOfy. *Lynis*, herramienta de auditoría de seguridad de sistemas. https://cisofy.com/lynis/
- OWASP. *OWASP ZAP*, versión 2.17. https://www.zaproxy.org/

## Anexos

_(logs largos y capturas extra; no cuentan para las 15 páginas)_
