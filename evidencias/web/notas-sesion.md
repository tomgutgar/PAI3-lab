# Notas de sesión — Parte 4 (pentesting web, Miguel)

Borrador en bruto para luego pasar al README/informe final. Se va ampliando a medida que avanzamos.

## Objetivo

- Repo original del equipo: `gti-sos/SOS2526-11` (asignatura SOS, curso anterior).
- Fork propio: `Ridawo/SOS-hardened`, clonado en `PAIS/PAI3/SOS-hardened`, rama `feat/pentesting-pai3`.
- Decisión: pentesting contra **SOS-hardened en local** (`localhost:8080`), nunca contra `https://sos2526-11.onrender.com` (es la URL real del equipo de 3, no solo mía).
- La guía oficial de la parte 4 sugiere DVWA; se usa SOS-hardened en su lugar porque cumple la regla de oro ("solo entornos propios o de pruebas") y ya tiene vulnerabilidades reales encontradas por revisión de código.

## Entorno

- Backend: Node/Express (`src/back/index.js`), front SvelteKit, BD NeDB, JWT.
- Arranque: `npm run build` (compila el front) + `npm start` → sirve en `http://localhost:8080`.
- `npm install` deja 35 vulnerabilidades en dependencias (11 moderate, 19 high, 5 critical) — anotado para la fase de hardening posterior, no se toca en el pentesting.
- ZAP 2.17.0 instalado vía `apt` (Kali). Proxy en `localhost:8082` (el 8081/8080 de la guía estaban ocupados).
- Tráfico capturado navegando con Firefox configurado con proxy manual → `localhost:8082`.

## Vulnerabilidades encontradas (revisión de código, por confirmar/documentar en ZAP)

1. **Broken Access Control (A01:2021)** — endpoints POST/PUT/DELETE de `api-JFM.js`, `api-JFM-v2.js`, `api-TGG.js`, `api-TGG-v2.js` sin ningún middleware de autenticación. Cualquiera puede borrar/modificar toda la colección de `literacy-rates` y `road-fatalities` sin credenciales.
2. **Secreto JWT hardcodeado y expuesto en repo público (A02:2021)** — `SECRET_KEY = "contraseñaMiguel"` en `src/back/api/api-MRG-v2.js:7` (y `index.js:41`). Al estar en un repo público de GitHub, cualquiera puede forjar un JWT válido (`jwt.sign({user:"admin"}, "contraseñaMiguel")`) y saltarse `verifyToken` sin pasar por `/login`.
3. **Credenciales hardcodeadas `admin`/`admin` (A07:2021)** — `api-MRG-v2.js:267`, ruta `/api/v2/alcohol-consumptions-per-capita/login`. **Confirmado en vivo**: login correcto desde el navegador con `admin`/`admin` tras dos intentos fallidos previos.
4. (Por confirmar) **Posible NoSQL injection** vía query string en NeDB — varios `GET` pasan `req.query.<campo>` directo a `db.find()`, y Express/`qs` permite sintaxis anidada (`?nation[$ne]=null`). Pendiente de probar.

## Evidencia capturada

- **Vulnerabilidad #3 (credenciales hardcodeadas)** — COMPLETA. Capturas en `PAI3/Evidencias pentesting web/Request.png` y `Response.png` (ruta fuera de `PAI3-lab`, mover a `PAI3-lab/evidencias/web/capturas/` antes de entregar). Request: `POST /api/v2/alcohol-consumptions-per-capita/login` con `{"username":"admin","password":"admin"}` (fila 36 de ZAP History). Response: `200 OK`, JWT emitido en el body. De propina, la respuesta confirma `Access-Control-Allow-Origin: *` (CORS abierto en toda la API).
- **Vulnerabilidad #1 (Broken Access Control, A01:2021)** — COMPLETA. Probada con ZAP → Requester: `DELETE http://localhost:8080/api/v2/road-fatalities HTTP/1.1` sin ninguna cabecera de autenticación → `200 OK`, `{"message":"OK: Todos los recursos eliminados."}`. Borra la colección entera sin credenciales. Captura pendiente de mover junto a las otras. Datos restaurados con `GET /api/v2/road-fatalities/loadInitialData` (204 registros).
- **Vulnerabilidad #2 (secreto JWT hardcodeado/expuesto, A02:2021)** — COMPLETA. Token forjado localmente con Node (`jwt.sign({user:"admin"}, "contraseñaMiguel", {expiresIn:"1h"})`), **sin pasar nunca por `/login`**. Probado con ZAP → Requester: `DELETE http://localhost:8080/api/v2/alcohol-consumptions-per-capita HTTP/1.1` + `authorization: Bearer <token forjado>` → `200 OK`, `{"message":"OK: Todos los recursos han sido eliminados."}`. Demuestra que `verifyToken` acepta cualquier token firmado con el secreto filtrado, sin validar que haya habido login real. Datos restaurados con `GET /api/v2/alcohol-consumptions-per-capita/loadInitialData` (150 registros).

**Las 3 vulnerabilidades obligatorias del entregable (b) están completas y documentadas.** Se añade una 4ª como extra.

- **Vulnerabilidad #4 (NoSQL injection, A03:2021, extra)** — CONFIRMADA por curl, pendiente de que Miguel la reproduzca en ZAP para la evidencia. `GET /api/v2/alcohol-consumptions-per-capita?nation=Spain` → 3 resultados (filtro normal). `GET /api/v2/alcohol-consumptions-per-capita?nation[$ne]=null` → **150 resultados** (toda la colección), saltándose el filtro inyectando el operador `$ne` de NeDB vía query string (Express/`qs` permite sintaxis de objeto anidado en la URL, y el valor se pasa sin sanear a `db.find()`). Mismo patrón probablemente replicable en otros campos/endpoints (`date_year`, `country`, etc. en JFM/TGG) — no probado todavía.

Pendiente: capturas de la #4 en ZAP, mover todas las capturas a `PAI3-lab/evidencias/web/capturas/`, plan de mitigación (apartado c), informe HTML de ZAP.

## Progreso de sesión (cronológico)

- Fork creado y renombrado a `Ridawo/SOS-hardened`, clonado en local, rama de trabajo creada.
- Proyecto instalado, compilado (`npm run build`) y arrancado en local (puerto 8080).
- ZAP instalado y abierto, sesión persistida con timestamp, proxy configurado en 8082.
- Navegado con Firefox vía proxy ZAP: home, `/login` (2 intentos fallidos + 1 correcto con `admin`/`admin`), sección Alcohol.
- Pendiente: revisar History de ZAP, capturar la petición de login como evidencia de la vulnerabilidad #3, probar #1 (DELETE sin auth) y #4 (NoSQL injection) desde ZAP, generar informe HTML de ZAP.
