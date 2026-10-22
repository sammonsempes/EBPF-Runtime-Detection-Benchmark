FROM ghcr.io/exein-io/pulsar:v0.10.1@sha256:d59aac7906e8c8c611aed5cbd1565d08936e800683d9d38f96842d3b86816d18 AS official

RUN mkdir -p /extract \
    && cp "$(command -v pulsard || find / -xdev -type f -name pulsard | head -n 1)" /extract/pulsard

FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends libsqlite3-0 libssl3t64 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=official /extract/pulsard /usr/bin/pulsard
COPY --from=official /var/lib/pulsar /var/lib/pulsar

ENTRYPOINT ["/usr/bin/pulsard"]
