FROM alpine:3.20 AS download

ARG KUNAI_VERSION=0.6.2
ARG KUNAI_SHA256_AMD64=cfcd7ee3594e1136290ef3327f1b5bfe550af0cda4fdf5cea46645254b3daba3
ARG KUNAI_SHA256_ARM64=fb14ac760c460dee7d43ee938a66e6f9ad5dba85571bf95ff24482ab8744aaf0
ARG TARGETARCH=amd64

COPY --from=certs . /usr/local/share/ca-certificates/extra/
RUN find /usr/local/share/ca-certificates/extra -type f \( -name '*.crt' -o -name '*.pem' \) -exec cat {} + >> /etc/ssl/certs/ca-certificates.crt \
    && apk add --no-cache curl \
    && find /usr/local/share/ca-certificates/extra -type f \( -name '*.crt' -o -name '*.pem' \) -exec cat {} + >> /etc/ssl/certs/ca-certificates.crt \
    && case "${TARGETARCH}" in \
         amd64) asset=kunai-amd64; sum="${KUNAI_SHA256_AMD64}" ;; \
         arm64) asset=kunai-aarch64; sum="${KUNAI_SHA256_ARM64}" ;; \
         *) echo "unsupported architecture ${TARGETARCH}" >&2; exit 1 ;; \
       esac \
    && curl -fsSL -o /kunai "https://github.com/kunai-project/kunai/releases/download/v${KUNAI_VERSION}/${asset}" \
    && echo "${sum}  /kunai" | sha256sum -c - \
    && chmod 0755 /kunai

FROM alpine:3.20

COPY --from=download /kunai /usr/bin/kunai

ENTRYPOINT ["/usr/bin/kunai"]
CMD ["run", "-c", "/etc/kunai/config.yaml"]
