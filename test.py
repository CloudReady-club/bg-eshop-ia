import subprocess
import re
import sys


def get_certificate(host, port=443):
    cmd = [
        "openssl",
        "s_client",
        "-connect",
        f"{host}:{port}",
        "-servername",
        host,
        "-showcerts",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, input="", timeout=30)
    out = (proc.stdout or "") + (proc.stderr or "")
    certs = re.findall(r"(-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----)", out, re.S)
    if not certs:
        raise RuntimeError("no certificates found; ensure 'openssl' is installed and reachable")
    return {"pem_chain": "\n\n".join(certs), "first_pem": certs[0]}


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "google.com"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443

    try:
        cert = get_certificate(host, port=port)
    except Exception as e:
        print(f"Error fetching certificate: {e}")
        raise

    print(cert["pem_chain"])
