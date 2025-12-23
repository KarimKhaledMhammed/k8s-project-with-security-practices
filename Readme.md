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

**Cosign verification (example):**
![Cosign Version](/assets/cosign-version.png)

**Cosign verification (example):**
![Cosign Version](/assets/cosign_verfication.png)

**Frontend Login Page (example):**
![App Login](/assets/app-login.png)


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
