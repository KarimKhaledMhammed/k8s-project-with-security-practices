🛡️ Secure 3-Tier Kubernetes Deployment (DevSecOps)

An opinionated, security-first deployment for a 3-tier web app (Frontend, Backend, Data). This repository shows how to combine Helm, strict Network Policies, image signing (Cosign), and init containers to achieve a production-ready, reproducible deployment.

---

## 🚀 Highlights

- **Zero-Trust Networking:** Namespace isolation and explicit NetworkPolicies (Frontend → Backend, Backend → Data).
- **Supply Chain Security:** Images are signed and verified with Cosign.
- **Infrastructure as Code:** Deployable via Helm chart `secure-app/` for repeatable installs.
- **Service Readiness:** Backend uses an Init Container to wait for Postgres and Redis.

---

## 📋 Table of Contents

1. [Architecture](#-architecture)
2. [Quickstart](#-quickstart)
3. [Security & Image Verification](#-security--image-verification)
4. [Testing](#-testing--validation)
5. [Screenshots](#-screenshots)
6. [Tech Stack](#-tech-stack)

---

## 🏗️ Architecture

Namespaces and purpose:

| Namespace | Purpose |
|---|---|
| `frontend-ns` | Nginx frontend + Ingress |
| `backend-ns`  | Flask API backend |
| `data-ns`     | PostgreSQL + Redis |

Traffic is restricted with NetworkPolicies to follow least-privilege principles.

---

## ⚡ Quickstart

Prerequisites: Kubernetes (Minikube or similar), Helm v3+, Cosign CLI, and an ingress controller.

1. Clone and enter repo
```bash
git clone https://github.com/karimkhaled02/k8s_project.git
cd k8s_project
```

2. Create Namespaces
```bash
kubectl create ns frontend-ns
kubectl create ns backend-ns
kubectl create ns data-ns
```

3. (Optional) Create Docker credentials for private images
```bash
kubectl create secret docker-registry my-docker-creds \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=YOUR_DOCKER_HUB_USER \
  --docker-password=YOUR_DOCKER_HUB_TOKEN \
  --namespace=backend-ns
```

4. Install via Helm
```bash
helm install secure-app ./secure-app --atomic
```

---

## 🔒 Security & Image Verification

All images are meant to be signed with Cosign. Use the included public key `cosign.pub` to verify images before applying them.

Offline verification examples:

```bash
# Verify Backend
COSIGN_OFFLINE=1 cosign verify --key cosign.pub karimkhaled02/k8s_front_back:backend-v1

# Verify Frontend
COSIGN_OFFLINE=1 cosign verify --key cosign.pub karimkhaled02/k8s_front_back:frontend-v1
```

Tip: Enforce verification in admission controllers (e.g., Kyverno, OPA/Gatekeeper) to block unsigned images at admission time.

### Enable Sigstore image verification

If you're using a `ClusterImagePolicy` (Sigstore) you may need to label namespaces so the policy applies. Example:

```bash
kubectl label namespace frontend-ns policy.sigstore.dev/include=true
kubectl label namespace backend-ns policy.sigstore.dev/include=true
```

The chart includes a sample public key in `secure-app/values.yaml` (under `security.publicKey`) used by the `ClusterImagePolicy` template.

### TLS: generate and install a cert (optional)

For local testing you can generate a self-signed certificate and create a TLS secret used by the ingress:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=myapp.local/O=DevSecOps"
kubectl create secret tls myapp-tls-secret --key tls.key --cert tls.crt -n frontend-ns
```

Alternatively, paste your cert/key into `secure-app/values.yaml` under `secrets.tlsCrt` and `secrets.tlsKey` before installing the chart.

---
## 🔐 Vault Integration

This project can integrate with HashiCorp Vault for secret management and to provide short-lived credentials to your backend. The following snippets show a minimal workflow for enabling Kubernetes auth and creating a role/policy for the `backend` service account in `backend-ns`.

1. Enable Kubernetes auth and configure the Kubernetes auth backend in Vault (example):

```bash
# On the Vault server: enable kubernetes auth
vault auth enable kubernetes

# Configure the Kubernetes auth method (use your cluster CA/token/service account)
vault write auth/kubernetes/config \
  token_reviewer_jwt="$TOKEN_REVIEWER_JWT" \
  kubernetes_host="$KUBE_HOST" \
  kubernetes_ca_cert=@/path/to/ca.crt
```

2. Create a policy that allows access to necessary secrets (example `backend-policy`):

```hcl
# backend-policy.hcl
path "secret/data/backend/*" {
  capabilities = ["read", "list"]
}
```

```bash
vault policy write backend-policy backend-policy.hcl
```

3. Create a role that maps a Kubernetes service account to the Vault policy:

```bash
vault write auth/kubernetes/role/backend-role \
  bound_service_account_names=backend-sa \
  bound_service_account_namespaces=backend-ns \
  policies=backend-policy \
  ttl=1h
```

4. From within Kubernetes, your backend pod (using `backend-sa`) can request a token from Vault and read secrets as allowed by `backend-policy`.

See the screenshots below for example Vault UI pages (login, dashboard, backend-role).

---
## 🧪 Testing & Validation

1. Sign-up flow (end-to-end test):

```bash
curl -X POST http://myapp.local/api/signup \
     -d "username=karim_final" \
     -d "password=success123"
```

Expected: "User karim_final Signed Up!"

2. Validate DB persistence

```bash
kubectl exec -it $(kubectl get pod -l app=postgres -n data-ns -o name) -n data-ns -- \
  psql -U postgres -c "SELECT * FROM users;"
```

---

## 🖼️ Screenshots
**Cosign version:**
![Cosign Version](/assets/cosign-version.svg)

**Cosign verification (example):**
![Cosign Version](/assets/cosign-version.svg)

**Frontend Login Page (example):**
![App Login](/assets/app-login.svg)

**Vault (examples):**
![Vault Login](/assets/vault-login.png)
![Vault Dashboard](/assets/vault-dashboard.png)
![Vault Backend Role](/assets/vault-backend-role.png)

_Note: Replace the placeholder PNGs in `/assets/` with your real screenshots (PNG/JPG) if you prefer higher-fidelity images._

Example (replace and commit):

```bash
cp ~/Downloads/vault-login.png assets/vault-login.png
cp ~/Downloads/vault-dashboard.png assets/vault-dashboard.png
cp ~/Downloads/vault-backend-role.png assets/vault-backend-role.png
git add assets/vault-*.png && git commit -m "chore: add vault screenshots" && git push
```
---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Orchestration | Kubernetes |
| IaC | Helm |
| Security | Cosign, Trivy, Network Policies |
| Backend | Python (Flask), Psycopg2 |
| Frontend | Nginx |

---

## 👨‍💻 Author

Karim Khaled Mohammed — Aspiring DevOps Engineer (Cloud Security, K8s Networking, CI/CD, DevSecOps)
