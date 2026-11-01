# Directivas aplicadas (justificación)

Una fila por directiva. Esto se copia tal cual al informe.

| Directiva | Valor | Riesgo que mitiga | Prueba que lo verifica |
|-----------|-------|-------------------|------------------------|
| HttpsOnlyMode | force_enabled | Tráfico sin cifrar / downgrade | badssl http.badssl.com |
| PasswordManagerEnabled | false | Robo de credenciales guardadas | No ofrece guardar login |
| ExtensionSettings | bloquear * + allowlist | Extensiones maliciosas | Instalar extensión → bloqueada |
| ... | ... | ... | ... |
