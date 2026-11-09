# Notas de sesión — Parte 4 (pentesting web, Miguel)

Borrador para pasar luego al README o al informe. Se amplía según avanzamos.

## Objetivo

El repo original del equipo es `gti-sos/SOS2526-11`, de la asignatura SOS del curso anterior. Hice un fork propio, `Ridawo/SOS-hardened`, clonado en `PAIS/PAI3/SOS-hardened` y con el trabajo en la rama `feat/pentesting-pai3`.

El pentesting va contra SOS-hardened en local (`localhost:8080`), nunca contra `https://sos2526-11.onrender.com`, que es la URL real del equipo de 3, no solo mía.

La guía oficial de la parte 4 sugiere usar DVWA. Uso SOS-hardened en su lugar porque cumple la regla de oro ("solo entornos propios o de pruebas") y ya tenía vulnerabilidades reales localizadas por revisión de código.

## Entorno

El backend es Node/Express (`src/back/index.js`), el front SvelteKit, la base de datos NeDB y la autenticación JWT. Arranca con `npm run build` (compila el front) y luego `npm start`, sirviendo en `http://localhost:8080`. `npm install` deja 35 vulnerabilidades en las dependencias (11 moderate, 19 high, 5 critical); lo anoto para la fase de hardening, en el pentesting no se toca.

ZAP 2.17.0 instalado con `apt` en Kali. El proxy quedó en `localhost:8082` porque el 8081 y el 8080 de la guía ya estaban ocupados. El tráfico se capturó navegando con Firefox configurado con ese proxy.

## Vulnerabilidades encontradas por revisión de código

1. Broken Access Control (A01:2021): los endpoints POST/PUT/DELETE de `api-JFM.js`, `api-JFM-v2.js`, `api-TGG.js` y `api-TGG-v2.js` no tienen ningún middleware de autenticación. Cualquiera puede borrar o modificar toda la colección de `literacy-rates` y `road-fatalities` sin credenciales.
2. Secreto JWT hardcodeado y expuesto en un repo público (A02:2021): `SECRET_KEY = "contraseñaMiguel"` en `src/back/api/api-MRG-v2.js:7` (y en `index.js:41`). Al estar en un repo público de GitHub, cualquiera puede forjar un JWT válido (`jwt.sign({user:"admin"}, "contraseñaMiguel")`) y saltarse `verifyToken` sin pasar por `/login`.
3. Credenciales hardcodeadas `admin`/`admin` (A07:2021), en `api-MRG-v2.js:267`, ruta `/api/v2/alcohol-consumptions-per-capita/login`. Confirmado en vivo con un login correcto desde el navegador tras dos intentos fallidos previos.
4. Posible NoSQL injection vía query string en NeDB, por confirmar: varios `GET` pasan `req.query.<campo>` directo a `db.find()`, y Express/`qs` permite sintaxis anidada (`?nation[$ne]=null`).

## Evidencia capturada

**Vulnerabilidad #3 (credenciales hardcodeadas).** Completa. Capturas: `#3-login-request.png` y `#3-login-response.png`, en `PAI3/Evidencias pentesting web/` (fuera de `PAI3-lab` por ahora; hay que moverlas a `PAI3-lab/evidencias/web/capturas/` antes de entregar). El request es `POST /api/v2/alcohol-consumptions-per-capita/login` con `{"username":"admin","password":"admin"}` (fila 36 del History de ZAP), y el response devuelve `200 OK` con el JWT en el body. De paso, el response confirma `Access-Control-Allow-Origin: *`, es decir, CORS abierto en toda la API.

**Vulnerabilidad #1 (Broken Access Control).** Completa, y ampliada el 6-nov con un barrido sistemático por los 6 endpoints de recurso (3 recursos × v1/v2), probando `DELETE` sin ninguna cabecera de autenticación en cada uno:

| Recurso | Versión | Resultado |
|---|---|---|
| alcohol-consumptions-per-capita | v1 | `200 OK`, sin protección |
| alcohol-consumptions-per-capita | v2 | `403 Forbidden`, protegido |
| literacy-rates | v1 | `200 OK`, sin protección |
| literacy-rates | v2 | `200 OK`, sin protección |
| road-fatalities | v1 | `200 OK`, sin protección |
| road-fatalities | v2 | `200 OK`, sin protección |

5 de 6 completamente abiertos; solo `alcohol v2` pide token (y esa "protección" tampoco vale, ver vulnerabilidad #2). Capturas: `#1-v1-alcohol-sin-auth.png`, `#1-v2-alcohol-protegido.png`, `#1-v1-literacy-sin-auth.png`, `#1-v2-literacy-sin-auth.png`, `#1-v1-road-sin-auth.png`, `#1-v2-road-sin-auth.png`. Todas las colecciones se restauraron después con `GET /api/<versión>/<recurso>/loadInitialData`.

**Vulnerabilidad #2 (secreto JWT expuesto).** Completa. Captura: `#2-jwt-forjado.png`. Generé el token con Node, en local, sin pasar nunca por `/login`: `jwt.sign({user:"admin"}, "contraseñaMiguel", {expiresIn:"1h"})`. Con ZAP, `DELETE http://localhost:8080/api/v2/alcohol-consumptions-per-capita HTTP/1.1` más la cabecera `authorization: Bearer <token forjado>` devuelve `200 OK` y borra los datos. Demuestra que `verifyToken` acepta cualquier token firmado con el secreto filtrado, sin comprobar que haya habido un login real. Datos restaurados con `GET /api/v2/alcohol-consumptions-per-capita/loadInitialData` (150 registros).

Nota del 6-nov, tras la mitigación: rotar el secreto en el código actual no basta por sí solo. El secreto viejo sigue siendo recuperable en el historial de git (commit `242c1a4`, confirmado con `git log --all -S "contraseñaMiguel"`), y el repo es público. No se reescribió el historial, porque afectaría a los clones de los compañeros; se trata el secreto viejo como comprometido para siempre, que es justo la razón de rotarlo y no solo corregir el valor en el HEAD actual.

Con esto ya están las 3 vulnerabilidades obligatorias del apartado (b). Añado una cuarta como extra:

**Vulnerabilidad #4 (NoSQL injection, A03:2021).** Completa. Capturas: `#4-filtro-normal.png` (`?nation=Spain`, 3 resultados, 342 bytes) y `#4-filtro-inyectado.png` (`?nation[$ne]=null`, 150 resultados, 17.148 bytes — el mismo tamaño que la colección sin filtrar, prueba de que el filtro se saltó por completo). El filtro se salta inyectando el operador `$ne` de NeDB por la query string, porque Express/`qs` admite sintaxis de objeto anidado en la URL y el valor llega sin sanear a `db.find()`. Es probable que el mismo patrón funcione en otros campos o endpoints (`date_year`, `country`... en JFM/TGG); no lo probé uno a uno, pero la corrección del 6-nov (`stringFilter`) se aplicó a todos los filtros de texto de los 6 ficheros de la API.

Aviso sobre el impacto real, para no exagerarlo en el informe: en este endpoint concreto (`GET`, público, sin autenticación) no hay ningún dato al que no se pudiera acceder ya pidiendo la colección sin filtro. El hallazgo no es "robo de datos", es que el código no valida el tipo de los parámetros de entrada, lo que permite inyectar operadores de NeDB. El riesgo real es que el mismo patrón de código está repetido en más sitios del proyecto, y si algún día se usara para filtrar algo sensible (por ejemplo, datos restringidos a un usuario), el mismo truco serviría para saltárselo.

**Confirmación por fuzzing en caja negra (6-nov)**, con el Fuzzer de ZAP sobre el parámetro `nation=Spain`, probando 5 operadores de NeDB: `$ne`, `$gt`, `$regex`, `$exists` y `$where`. Resultado: la petición de control da 342 bytes (3 resultados de España); **las 5 con operador inyectado dan 17.148 bytes**, el tamaño exacto de la colección completa sin filtrar. Captura: `#4-fuzzer-nosql-caja-negra.png`. No es solo `$ne` — el campo no está saneado frente a ningún operador. `$where` en NeDB puede ejecutar JavaScript arbitrario si se le pasa una función; aquí solo se probó con un valor simple (`=1`), así que no se ha demostrado ejecución de código, solo que el campo también acepta ese operador sin más — posible vía adicional a explorar, no explotada por no ser necesaria para el entregable.

**Dependencias (`npm audit`, 6-nov).** 35 vulnerabilidades (11 moderate, 19 high, 5 critical). La más relevante: `nedb` (la propia base de datos de la app, no una herramienta de test) tiene una de severidad **crítica** (Prototype Pollution, GHSA-339j-hqgx-qrrx) **sin parche disponible**. El resto de críticas/altas vienen sobre todo de `newman`/`postman-*` (dependencias de test, no de producción). Log completo en `evidencias/web/npm-audit-2026-11-06.log`.

## Apartado (c) — mitigación, antes/después (6-nov)

Cambios en `SOS-hardened` (rama `feat/pentesting-pai3`):

- Nuevo módulo `src/back/api/security.js`: `verifyToken` (lee el secreto de `JWT_SECRET` en `.env`, ya no hardcodeado), `ADMIN_USER`/`ADMIN_PASSWORD` desde `.env`, y `stringFilter()` para rechazar valores de filtro que no sean un string plano (bloquea la inyección de operadores NoSQL).
- `verifyToken` aplicado a **todos** los `POST`/`PUT`/`DELETE` de recurso en los 6 ficheros de la API (antes solo protegía uno de seis).
- Login (`api-MRG-v2.js`) usa `ADMIN_USER`/`ADMIN_PASSWORD`/`JWT_SECRET` del `.env` en vez de credenciales y secreto en el código.
- Filtros `nation`/`country`/`income_level`/`traffic_side` saneados con `stringFilter` en los 6 ficheros.
- `.env.example` actualizado documentando `JWT_SECRET`, `ADMIN_USER`, `ADMIN_PASSWORD` (con el comando para generarlos). `.env` real generado en local, no se commitea.
- `index.js`: eliminado el `SECRET_KEY` hardcodeado que no se usaba.

**Resultados (antes → después), repitiendo exactamente los mismos ataques:**

| Vulnerabilidad | Antes | Después |
|---|---|---|
| #1 Acceso sin auth | 5/6 endpoints en `200 OK` sin credenciales | 6/6 en `403 Forbidden` |
| #2 Secreto JWT filtrado | Token forjado con `contraseñaMiguel` aceptado (`200 OK`) | Rechazado (`401`); secreto rotado (aleatorio, 48 bytes) y fuera del código |
| #3 Credenciales hardcodeadas | `admin`/`admin` funcionaba | Rechazado (`401`); credenciales nuevas en `.env`, generadas al azar |
| #4 Inyección NoSQL | `?nation[$ne]=Spain` cambiaba el resultado | Operador ignorado: verificado comparando `?nation[$ne]=Spain` (150 resultados) contra `?nation=Spain` eliminado (sin filtro, también 150) — si el operador llegara a NeDB darían 147, no 150 |

Funcionalidad legítima verificada intacta: login con las credenciales nuevas devuelve un token válido, y ese token permite un `PUT` real (`200 OK`).

**Payload propio** guardado en `web/payloads/nosql.txt` (los 5 operadores usados en el Fuzzer de la #4), junto a `sqli.txt` y `xss.txt`.

**Informe HTML de ZAP** generado: `evidencias/web/2026-11-06-ZAP-Report-localhost.html` (plantilla "Risk and Confidence HTML"). Incluye algo de ruido de dominios de publicidad/tracking (adsrvr, doubleclick, facebook...) que se colaron en el historial por otras pestañas abiertas con el proxy puesto durante la sesión — la pestaña "Filter" del generador de ZAP solo filtra por riesgo/confianza, no por URL/sitio, así que no se pudo excluir sin borrar manualmente cada dominio del árbol de Sites. No afecta a los hallazgos de `localhost:8080`, que están igualmente documentados ahí y, sobre todo, en las capturas dedicadas de cada vulnerabilidad.

## Progreso de la sesión

Creé y renombré el fork a `Ridawo/SOS-hardened`, lo cloné en local y abrí la rama de trabajo. Instalé el proyecto, lo compilé con `npm run build` y lo arranqué en local, puerto 8080. Instalé ZAP, abrí sesión persistida con timestamp y dejé el proxy en 8082. Navegué con Firefox a través del proxy: home, `/login` (dos intentos fallidos y uno correcto con `admin`/`admin`), sección Alcohol.

Pendiente al cierre del 5-nov (hecho el 6-nov): revisar el History de ZAP, capturar la petición de login como evidencia de la #3, probar la #1 y la #4 desde ZAP, generar el informe HTML.
