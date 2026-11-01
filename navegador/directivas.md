# Directivas aplicadas (justificación)

Una fila por directiva. Esto se copia tal cual al informe.

| Directiva | Valor | Riesgo que mitiga | Prueba que lo verifica |
|-----------|-------|-------------------|------------------------|
| HttpsOnlyMode | force_enabled | Tráfico sin cifrar / downgrade | badssl, http.badssl.com |
| SSLVersionMin | tls1.2 | Protocolos TLS obsoletos | badssl (tls-v1-0) |
| PasswordManagerEnabled | false | Robo de credenciales guardadas | No ofrece guardar login |
| EnableTrackingProtection | strict + crypto/fingerprint | Rastreo y huella digital | Cover Your Tracks (EFF) |
| DNSOverHTTPS | Enabled + Locked | Espionaje de DNS | 1.1.1.1/help |
| ExtensionSettings | bloquear * + allowlist | Extensiones maliciosas | Instalar una → bloqueada |
| Permissions (cam/mic/geo/notif) | BlockNewRequests | Permisos intrusivos | La web no puede pedirlos |
| BlockAboutConfig | true | Usuario saltándose la política | about:config bloqueado |
| DisableTelemetry | true | Fuga de datos de uso | — |
