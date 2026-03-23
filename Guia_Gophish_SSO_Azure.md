================================================================================
                    GUÍA COMPLETA: GOPHISH CON SSO AZURE AD
                     Instalación Local y Azure VM
================================================================================

================================================================================
TABLA DE CONTENIDOS
================================================================================

1. INFORMACIÓN GENERAL
2. PARTE 1: PRUEBA LOCAL
3. PARTE 2: INSTALACIÓN EN AZURE VM
4. INSTALACIÓN DEL CÓDIGO NUEVO
5. AZURE - ESPECIFICACIONES RECOMENDADAS
6. TROUBLESHOOTING
7. COMANDOS RÁPIDOS
8. CHECKLIST FINAL

================================================================================
1. INFORMACIÓN GENERAL
================================================================================

PROPÓSITO:
----------
Este Documento describe cómo implementar y probar el módulo de SSO (Single 
Sign-On) con Azure Active Directory en Gophish, tanto en un entorno local 
como en una máquina virtual en Microsoft Azure.

REPOSITORIO:
------------
- GitHub: https://github.com/polidisio/gophish
- Rama principal SSO: feature/azure-sso
- Rama Analytics: feature/modern-dashboard-analytics

CARACTERÍSTICAS IMPLEMENTADAS:
-------------------------------
- Login SSO con Azure AD (OAuth2/OIDC)
- Sincronización automática de usuarios desde Microsoft Graph API
- Panel de configuración en la UI
- Migraciones de base de datos (SQLite y MySQL)

REQUISITOS PREVIOS:
-------------------
- Cuenta de Azure (puede ser trial gratuito)
- Go 1.26+ instalado
- Navegador web moderno
- Acceso a Azure Portal con permisos para crear App Registrations

ARQUITECTURA:
-------------
[Usuario] → [Gophish Azure VM] → [Azure AD] → [Gophish]
                ↓
           [Microsoft Graph API] (para sync de usuarios)

================================================================================
2. PARTE 1: PRUEBA LOCAL
================================================================================

PASO 1: CREAR APP EN AZURE AD
------------------------------

1.1 Acceder al Portal de Azure
URL: https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps

1.2 Nueva Registración
- Click en "New registration"
- Name: Gophish SSO
- Supported account types: "Accounts in this organizational directory only"
- Redirect URI: Web → http://localhost:3333/oauth/callback
- Click "Register"

1.3 Copiar IDs
Guardar los siguientes valores:
- Application (client) ID: _______________
- Directory (tenant) ID: _______________

1.4 Crear Client Secret
- Ir a "Certificates & secrets"
- Click "New client secret"
- Description: Gophish Production
- Expires: 12 o 24 meses
- COPIAR EL VALOR: _______________

1.5 Configurar Redirect URIs
- Ir a "Authentication"
- Click "Add a platform" → "Web"
- Redirect URIs: http://localhost:3333/oauth/callback
- Implicit grant: marcar ID tokens

1.6 Permisos API
- Ir a "API permissions"
- Click "Add a permission" → "Microsoft Graph"
- Delegated permissions: User.Read, Profile, Email
- Application permissions: Directory.Read.All
- Click "Grant admin consent"


PASO 2: CONFIGURAR GOPHISH LOCAL
---------------------------------

2.1 Compilar Gophish
  cd ~/.openclaw/workspace/gophish
  go build -o gophish

2.2 Ejecutar Migraciones
  sqlite3 gophish.db < db/db_sqlite3/migrations/20260302000000_modern_analytics.sql
  sqlite3 gophish.db < db/db_sqlite3/migrations/20260302000001_azure_sso.sql

2.3 Iniciar Gophish
  ./gophish

2.4 Acceder a Gophish
- Abrir navegador: http://localhost:3333
- Login: admin / (password del log)

2.5 Configurar SSO
1. Ir a Settings → SSO Configuration
2. Rellenar formulario
3. Marcar Enable SSO Login
4. Click Save

2.6 Probar Login SSO
1. Hacer logout
2. Verificar que aparece botón "Login with Microsoft"
3. Click → redirige a Microsoft
4. Login con cuenta de Azure AD
5. Redirigir a dashboard de Gophish


PASO 3: PROBAR SYNC DE USUARIOS
--------------------------------

3.1 En la UI de SSO Settings
1. Click "Sync Users from Azure AD"
2. Verificar que aparecen usuarios
3. Revisar tabla azure_ad_users en DB

3.2 Verificar con API
  API_KEY="tu_api_key_aqui"
  curl -H "Authorization: Bearer $API_KEY" \
       http://localhost:3333/api/azuread/users


================================================================================
3. PARTE 2: INSTALACIÓN EN AZURE VM
================================================================================

ESPECIFICACIONES RECOMENDADAS
-----------------------------
- Suscripción: Azure Subscription (trial o paid)
- Sistema Operativo: Ubuntu 22.04 LTS
- VM recomendada: Standard_B2s (2 vCPU, 4GB RAM)
- Costo estimado: ~$10-15/mes
- Ubicación: West Europe o la más cercana

PASO 1: CREAR VM EN AZURE
--------------------------

1.1 Desde Portal Azure
Ir a: Virtual machines → Create → Ubuntu Server 22.04 LTS

1.2 Configuración de la VM
- Resource Group: gophish-rg (crear nuevo)
- VM name: gophish-vm
- Region: West Europe
- Image: Ubuntu 22.04 LTS - x64
- Size: Standard_B2s (2 vCPU, 4GB RAM)
- Authentication type: SSH key
- Inbound ports: 22, 80, 443, 3333, 8080

1.3 Conectar por SSH
  ssh gophish@ip-publica-vm


PASO 2: INSTALLAR GOPHISH EN VM
--------------------------------

2.1 Actualizar sistema
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y curl wget git build-essential

2.2 Instalar Go
  wget https://go.dev/dl/go1.26.0.linux-amd64.tar.gz
  sudo tar -C /usr/local -xzf go1.26.0.linux-amd64.tar.gz
  echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
  source ~/.bashrc

2.3 Instalar SQLite
  sudo apt install -y sqlite3

2.4 Clonar repositorio
  git clone https://github.com/polidisio/gophish.git
  cd gophish
  git checkout feature/azure-sso

2.5 Compilar
  go build -o gophish

2.6 Crear directorio de trabajo
  sudo mkdir -p /opt/gophish
  sudo cp gophish /opt/gophish/


PASO 3: CONFIGURAR AZURE AD PRODUCCIÓN
---------------------------------------

3.1 Actualizar Redirect URIs en Azure
Cambiar de: http://localhost:3333/oauth/callback
A: https://tu-dominio.com/oauth/callback

3.2 Actualizar Gophish config
{
    "admin_server": {
        "listen_url": "0.0.0.0:3333"
    },
    "phish_server": {
        "listen_url": "0.0.0.0:8080"
    },
    "db_name": "sqlite3",
    "db_path": "/opt/gophish/gophish.db"
}


PASO 4: CREAR SERVICIO SYSTEMD
-------------------------------

4.1 Crear servicio
sudo nano /etc/systemd/system/gophish.service

[Unit]
Description=Gophish Phishing Framework
After=network.target

[Service]
Type=simple
User=gophish
WorkingDirectory=/opt/gophish
ExecStart=/opt/gophish/gophish
Restart=always

[Install]
WantedBy=multi-user.target

4.2 Habilitar servicio
  sudo systemctl daemon-reload
  sudo systemctl enable gophish
  sudo systemctl start gophish
  sudo systemctl status gophish


PASO 5: CONFIGURAR FIREWALL AZURE
----------------------------------

En Portal Azure: VM → Networking → Inbound security rules

| Priority | Name          | Port  | Action |
|----------|---------------|-------|--------|
| 100      | HTTP          | 80    | Allow  |
| 110      | HTTPS         | 443   | Allow  |
| 120      | Gophish Admin | 3333  | Allow  |
| 130      | Phish Server  | 8080  | Allow  |


PASO 6: VERIFICAR FUNCIONAMIENTO
---------------------------------

6.1 Probar endpoints
  curl http://localhost:3333
  sudo journalctl -u gophish -f

6.2 Probar desde navegador
- Admin: https://tu-dominio.com:3333
- Phishing: http://tu-dominio.com:8080

6.3 Probar SSO
1. Hacer logout
2. Login con Microsoft
3. Verificar que funciona


================================================================================
4. INSTALACIÓN DEL CÓDIGO NUEVO
================================================================================

REPOSITORIO GITHUB
URL: https://github.com/polidisio/gophish

RAMAS DISPONIBLES
------------------
1. feature/modern-dashboard-analytics
   - Dashboard moderno con métricas avanzadas
   - Gráficos Chart.js
   - Score de susceptibilidad por usuario

2. feature/azure-sso
   - Integración SSO Azure AD
   - Sync automático de usuarios
   - Panel de configuración

CLONAR Y COMPILAR
------------------
# Clonar
git clone https://github.com/polidisio/gophish.git
cd gophish

# Cambiar a rama SSO
git checkout feature/azure-sso

# Compilar
go build -o gophish


================================================================================
5. AZURE - ESPECIFICACIONES RECOMENDADAS
================================================================================

VM RECOMENDADA
--------------
- Nombre: gophish-vm
- OS: Ubuntu 22.04 LTS
- Tamaño: Standard_B2s (2 vCPU, 4GB RAM)
- Disco: 30 GB SSD
- Red: Nueva VNET con NAT

COSTOS ESTIMADOS (West Europe)
-------------------------------
- VM B2s: ~€8.50/mes
- Discos: ~€3.00/mes
- Transferencia: ~€1.00/mes
- IP Pública: ~€3.00/mes
- TOTAL: ~€15.50/mes


================================================================================
6. TROUBLESHOOTING
================================================================================

ERROR: "invalid_client"
Solución: Verificar Client ID y Secret en Azure

ERROR: "AADSTS50011"
Solución: Verificar Redirect URI en Azure

ERROR: "No access token"
Solución: Verificar permisos de API en Azure

ERROR: "connection refused" en VM
Solución: sudo systemctl status gophish

ERROR: SSL certificate error
Solución: sudo certbot renew


================================================================================
7. COMANDOS RÁPIDOS
================================================================================

GESTIÓN DE SERVICIO
-------------------
sudo systemctl restart gophish
sudo systemctl status gophish
sudo journalctl -u gophish -f

GESTIÓN DE BASE DE DATOS
------------------------
cp /opt/gophish/gophish.db /opt/gophish/backup-$(date +%Y%m%d).db

VERIFICACIÓN
------------
curl -I http://localhost:3333
curl -I http://localhost:8080


================================================================================
8. CHECKLIST FINAL
================================================================================

PARTE 1: LOCAL
[ ] App creada en Azure
[ ] Client ID copiado
[ ] Client Secret copiado
[ ] Tenant ID copiado
[ ] Permisos API otorgados
[ ] Gophish compilado
[ ] Migraciones ejecutadas
[ ] SSO configurado
[ ] Login SSO funciona
[ ] User sync funciona

PARTE 2: AZURE VM
[ ] VM creada
[ ] SSH funciona
[ ] Gophish instalado
[ ] Migraciones ejecutadas
[ ] SSO configurado
[ ] Login SSO funciona
[ ] Firewall configurado
[ ] SSL configurado

================================================================================
Documento creado: Marzo 2026
Versión: 1.0
Autor: Aria (Asistente AI)
Repositorio: https://github.com/polidisio/gophish
================================================================================
