# Enlace publico fijo (espanol / Peru)

`trycloudflare.com` no permite elegir nombre.  
Para un link tipo `triaje-virtual-peru.tudominio.pe`, usa Tunnel nombrado de Cloudflare.

## 1) En Cloudflare (una sola vez)

1. Agrega tu dominio (ejemplo: `tudominio.pe`) a Cloudflare DNS.
2. Crea un Tunnel en Zero Trust:
   - `Networks` -> `Tunnels` -> `Create tunnel`.
3. Crea un Public Hostname para el tunnel:
   - Hostname: `triaje-virtual-peru`
   - Domain: `tudominio.pe`
   - Service: `http://frontend:80`
4. Copia el token del tunnel.

## 2) En este proyecto

1. En PowerShell, define el token:

```powershell
$env:CLOUDFLARE_TUNNEL_TOKEN="AQUI_TU_TOKEN"
```

2. Levanta servicios:

```powershell
docker compose up -d --build backend frontend
docker compose --profile share up -d share
```

3. Revisa logs del tunnel:

```powershell
docker logs triage-share --tail 100
```

## URL final

La URL publica sera la que configuraste:

`https://triaje-virtual-peru.tudominio.pe`
