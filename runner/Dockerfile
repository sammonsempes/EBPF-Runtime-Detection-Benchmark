FROM python:3.12-slim

ARG HELM_VERSION=3.16.4
ARG KUBECTL_VERSION=1.33.1
ARG TARGETARCH=amd64

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

COPY --from=certs . /usr/local/share/ca-certificates/extra/
RUN update-ca-certificates

RUN python - <<'EOF'
import hashlib
import io
import os
import tarfile
import urllib.request

arch = os.environ.get("TARGETARCH", "amd64")
helm = os.environ["HELM_VERSION"]
kubectl = os.environ["KUBECTL_VERSION"]


def fetch(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def verify(data, checksum_url):
    expected = fetch(checksum_url).decode().split()[0]
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise SystemExit(f"checksum mismatch for {checksum_url}: {actual} != {expected}")


archive_url = f"https://get.helm.sh/helm-v{helm}-linux-{arch}.tar.gz"
archive = fetch(archive_url)
verify(archive, archive_url + ".sha256sum")
with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
    member = bundle.extractfile(f"linux-{arch}/helm")
    with open("/usr/local/bin/helm", "wb") as target:
        target.write(member.read())

binary_url = f"https://dl.k8s.io/release/v{kubectl}/bin/linux/{arch}/kubectl"
binary = fetch(binary_url)
verify(binary, binary_url + ".sha256")
with open("/usr/local/bin/kubectl", "wb") as target:
    target.write(binary)

for path in ("/usr/local/bin/helm", "/usr/local/bin/kubectl"):
    os.chmod(path, 0o755)
EOF

WORKDIR /opt/runner
COPY pyproject.toml ./
COPY bench ./bench
RUN pip install --no-cache-dir ".[test,k8s]"

WORKDIR /bench
ENTRYPOINT ["python", "-m", "bench"]
CMD ["--help"]
