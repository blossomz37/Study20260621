# Static-server image for the BookHub site on Railway.
# Railway runs containers (not static hosting like GitHub Pages), so we serve
# demo/books/ with Caddy on the platform-provided $PORT. demo/books/index.html
# redirects "/" to the gallery at /site/. Caddy sets correct MIME (incl. image/webp).
FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY demo/books /srv
EXPOSE 8080
# (base image's entrypoint runs: caddy run --config /etc/caddy/Caddyfile --adapter caddyfile)
