# Parte 4 — Auditoría web (OWASP ZAP)

Tres entregas: (a) trazabilidad HTTP/HTTPS por proxy SIN modificar, (b) ≥ 3 vulns del OWASP Top 10 explotadas en DVWA, (c) plan de mitigación.

## Montar la web de pruebas

```bash
docker compose up -d          # DVWA en http://localhost:8080  (admin/password)
```

## ZAP

1. Proxy en `localhost:8081` (Options → Network → Local Servers/Proxies).
2. Guardar el certificado raíz (Dynamic SSL Certificates) e importarlo en el navegador como CA.
3. Navegador → proxy `localhost:8081` (o usar "Manual Explore" de ZAP).
4. Trazabilidad: navegar, pestaña History, abrir un login POST (sin modificar nada).
5. Vulnerabilidades: Breakpoint o Fuzzer (jbrofuzz → SQL Injection). Filas "Reflected/Found" = interesantes.
6. Mitigación: subir el nivel de DVWA a High/Impossible y repetir → ya no funciona.

Vulns objetivo: SQLi + XSS reflejado + XSS almacenado (las 3 obligatorias); Path Traversal y CSRF suman.

Evidencias: Report → Generate HTML Report, session de ZAP, peticiones exportadas → `../evidencias/web/`.
