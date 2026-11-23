# Remove X-Robots-Tag from www-docs

The documents served by `www-docs` (uploaded files) must always be available and indexable, so the
conditional `X-Robots-Tag: noindex, nofollow` (added in spec 009, `BLOCK_ROBOTS`) now applies only to
`www-static` (app).

## Changes

- `conf/nginx/docs/docs.conf`: removed `include /etc/nginx/robots.conf;` and `add_header X-Robots-Tag $robots_tag always;`
- `docker-compose.yml` (`www-docs`): removed the `robots.conf.template` mount and the `BLOCK_ROBOTS` /
  `NGINX_ENVSUBST_OUTPUT_DIR` env vars (no templates are rendered there anymore)
- `README.md` and `.env-TEMPLATE`: `BLOCK_ROBOTS` documented as app-only; www-docs never sends the header
- `www-static` (`app.conf`) and `robots.conf.template` unchanged

## Verification

- `nginx -t` OK on `nginx:1.30-alpine` with `conf/nginx/docs`
- `IMAGE_TAG=x docker compose config -q` OK
- Throwaway www-docs container with `BLOCK_ROBOTS=true`: 200 and 404 responses carry the security headers and no `X-Robots-Tag`
