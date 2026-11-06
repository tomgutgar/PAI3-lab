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

**Vulnerabilidad #1 (Broken Access Control).** Completa. Captura: `#1-acceso-sin-auth.png`. La probé con ZAP, pestaña Requester: `DELETE http://localhost:8080/api/v2/road-fatalities HTTP/1.1` sin ninguna cabecera de autenticación, y devuelve `200 OK` con `{"message":"OK: Todos los recursos eliminados."}`. Borra la colección entera sin credenciales. Los datos se restauraron después con `GET /api/v2/road-fatalities/loadInitialData` (204 registros).

**Vulnerabilidad #2 (secreto JWT expuesto).** Completa. Captura: `#2-jwt-forjado.png`. Generé el token con Node, en local, sin pasar nunca por `/login`: `jwt.sign({user:"admin"}, "contraseñaMiguel", {expiresIn:"1h"})`. Con ZAP, `DELETE http://localhost:8080/api/v2/alcohol-consumptions-per-capita HTTP/1.1` más la cabecera `authorization: Bearer <token forjado>` devuelve `200 OK` y borra los datos. Demuestra que `verifyToken` acepta cualquier token firmado con el secreto filtrado, sin comprobar que haya habido un login real. Datos restaurados con `GET /api/v2/alcohol-consumptions-per-capita/loadInitialData` (150 registros).

Con esto ya están las 3 vulnerabilidades obligatorias del apartado (b). Añado una cuarta como extra:

**Vulnerabilidad #4 (NoSQL injection, A03:2021).** Completa. Capturas: `#4-filtro-normal.png` (`?nation=Spain`, 3 resultados, 342 bytes) y `#4-filtro-inyectado.png` (`?nation[$ne]=null`, 150 resultados, 17.148 bytes — el mismo tamaño que la colección sin filtrar, prueba de que el filtro se saltó por completo). El filtro se salta inyectando el operador `$ne` de NeDB por la query string, porque Express/`qs` admite sintaxis de objeto anidado en la URL y el valor llega sin sanear a `db.find()`. Es probable que el mismo patrón funcione en otros campos o endpoints (`date_year`, `country`... en JFM/TGG), no lo he probado todavía.

Aviso sobre el impacto real, para no exagerarlo en el informe: en este endpoint concreto (`GET`, público, sin autenticación) no hay ningún dato al que no se pudiera acceder ya pidiendo la colección sin filtro. El hallazgo no es "robo de datos", es que el código no valida el tipo de los parámetros de entrada, lo que permite inyectar operadores de NeDB. El riesgo real es que el mismo patrón de código está repetido en más sitios del proyecto, y si algún día se usara para filtrar algo sensible (por ejemplo, datos restringidos a un usuario), el mismo truco serviría para saltárselo. También abre la puerta a operadores más peligrosos, como `$regex`, que se podría usar para provocar una denegación de servicio con una expresión cara de evaluar.

Queda pendiente: mover las 6 capturas a `PAI3-lab/evidencias/web/capturas/`, el plan de mitigación del apartado (c) y el informe HTML de ZAP. También quedan por hacer (opcional, refuerza el informe): dos pruebas negativas de control — bypass de login con operadores NoSQL en el body (`{"username":{"$ne":null},...}`, no debería funcionar por la comparación estricta `===`) y un intento de `$where` directo (no debería funcionar porque el código nunca pasa `req.query` entero a `db.find()`) — y confirmar la #4 también por fuzzing de caja negra con el Fuzzer de ZAP, sin partir del código fuente.

## Progreso de la sesión

Creé y renombré el fork a `Ridawo/SOS-hardened`, lo cloné en local y abrí la rama de trabajo. Instalé el proyecto, lo compilé con `npm run build` y lo arranqué en local, puerto 8080. Instalé ZAP, abrí sesión persistida con timestamp y dejé el proxy en 8082. Navegué con Firefox a través del proxy: home, `/login` (dos intentos fallidos y uno correcto con `admin`/`admin`), sección Alcohol.

Pendiente: revisar el History de ZAP, capturar la petición de login como evidencia de la #3, probar la #1 y la #4 desde ZAP, generar el informe HTML.
