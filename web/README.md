# Parte 4 — Auditoría web (OWASP ZAP) · Persona 3

> Tres cosas que entregar: **(a)** demostrar que el tráfico HTTP/HTTPS pasa por el proxy ZAP **sin modificarlo**, **(b)** encontrar y explotar **≥ 3 vulnerabilidades del OWASP Top 10** en una web de pruebas y **(c)** proponer un **plan de mitigación**.

## Qué necesitas saber

- **DAST** = probar la web desde fuera, como un atacante, sin ver el código (caja negra). Es lo que hacemos.
- **OWASP ZAP** se pone entre el navegador y la web (proxy). Ve, registra y puede modificar cada petición.
- Para leer HTTPS, ZAP genera certificados al vuelo firmados por su propia CA → hay que **importar su certificado raíz** en el navegador, si no salen avisos.
- **Fuzzing** = repetir una petición muchas veces cambiando un parámetro por cadenas de ataque de un diccionario.
- **OWASP Top 10**: usa la edición **2021** (la "2023" del PDF es la de APIs). Dilo en el informe.

## Paso 0 — Montar la web de pruebas (DVWA)

Nunca se ataca una web real. Usamos **DVWA** (una página por vulnerabilidad, con niveles de seguridad para el "antes/después"):

```bash
docker run --rm -it -p 8080:80 vulnerables/web-dvwa
# Navegador: http://localhost:8080  (admin / password → "Create / Reset Database")
```

## Paso 1 — ZAP como proxy

1. Instala ZAP (https://www.zaproxy.org/download/ ; necesita Java, ya está en el equipo).
2. Options → Network → Local Servers/Proxies: dirección `localhost`, puerto **8081**.
3. Options → Dynamic SSL Certificates → **Save** el certificado raíz.
4. Impórtalo en Firefox: Certificate Manager → Authorities → Import → marca "Trust this CA to identify websites".
5. Apunta el navegador al proxy `localhost:8081` (lo más fácil: botón **"Manual Explore"** de ZAP, que abre un navegador ya configurado).

## Paso 2 — Entrega (a): trazabilidad SIN modificar

Navega por DVWA, haz un login. En la pestaña **History** verás cada petición/respuesta. Abre un login POST y enseña cabeceras y parámetros (usuario/contraseña). **No modifiques nada**: aquí solo demuestras que ves el tráfico. Captura/exporta esas peticiones.

## Paso 3 — Entrega (b): 3+ vulnerabilidades (en DVWA)

| Vulnerabilidad | OWASP 2021 | Cómo | Qué demuestra |
|----------------|-----------|------|----------------|
| **SQL Injection** | A03 | Página "SQL Injection": Fuzzer sobre `id` con `jbrofuzz → SQL Injection` | Sacar usuarios/hashes con `1' OR '1'='1` |
| **XSS reflejado** | A03 | Página "XSS (Reflected)": `<script>alert(1)</script>` | El navegador ejecuta tu código |
| **XSS almacenado** | A03 | Página "XSS (Stored)": guardar el script | Ataca a quien abra la página |

Con estas tres cubres las obligatorias. *Path Traversal* (File Inclusion, `?page=../../../../etc/passwd`) y *CSRF* suben nota si te sobra tiempo.

**Cómo fuzzear**: botón derecho sobre una petición con parámetros → **Fuzz** → selecciona el parámetro → Payloads → Add → File Fuzzer → `jbrofuzz → SQL Injection` (o usa `payloads/sqli.txt`) → Start Fuzzer. Las filas marcadas **Reflected**/**Found** son las interesantes.

## Paso 4 — Entrega (c): mitigación

Sube el nivel de DVWA (DVWA Security → "High" / "Impossible"), repite el ataque y enseña que **ya no funciona**. Explica por qué (consultas parametrizadas, validación de entrada, escape de salida, token CSRF).

## Qué entregar

- Session de ZAP o export de las peticiones; captura del certificado raíz importado; informe HTML de ZAP (Report → Generate HTML Report). Todo a `evidencias/web/`.
- Los payloads propios (`payloads/`).
- En el informe: la demo de trazabilidad, una ficha por vulnerabilidad (petición, payload, resultado, captura) y el plan de mitigación con el "antes/después" del nivel de DVWA.
