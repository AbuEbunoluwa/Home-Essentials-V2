# 🏠 Masterpiece Home Essentials Marketplace

A production-grade e-commerce web app for home essential products, deployed on AWS EKS using a full DevOps stack.

## 🛠 Tech Stack
- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **Container**: Docker
- **Orchestration**: Kubernetes (AWS EKS)
- **Package Manager**: Helm
- **Infrastructure**: Terraform
- **CI/CD**: GitHub Actions
- **GitOps**: ArgoCD
- **Monitoring**: Prometheus + Grafana

## 📦 30 Products Across 9 Categories
- Living Room — Sofa, Coffee Table, Dining Table, Curtains, Wall Clock, Floor Lamp
- Bedroom — Mattress, Bed Frame, Wardrobe, Nightstand
- Kitchen — Air Fryer, Blender, Microwave, Kettle, Knife Set, Dish Rack
- Bathroom — Mirror, Towel Set
- Office — Chair, Bookshelf
- Kids Room — Toy Bin, Kids Desk, Baby Monitor
- Security — Smart Doorbell, Smart Thermostat
- Laundry — Steam Iron, Laundry Basket
- Garage — Tool Organizer, Garden Hose
- Cleaning — Vacuum Cleaner

## 🚀 Live API
- Base URL: http://a04ee986f249e49dd8e8deedfb75a5da-1246131963.us-east-1.elb.amazonaws.com
- API Docs: http://a04ee986f249e49dd8e8deedfb75a5da-1246131963.us-east-1.elb.amazonaws.com/docs

## 🔑 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Welcome message |
| GET | /health | Health check |
| GET | /products | Get all products |
| GET | /products?category=Kitchen | Filter by category |
| GET | /products/{id} | Get single product |
| GET | /categories | Get all categories |
| POST | /checkout | Place an order |
| GET | /orders | Get all orders |

## 📁 Project Structure
home-essentials/
├── app.py                   # FastAPI application
├── front/index.html         # Frontend
├── Dockerfile               # Container build
├── requirements.txt         # Python dependencies
├── helm/                    # Kubernetes Helm chart
├── terraform-local/         # AWS infrastructure (Terraform)
├── argocd/                  # GitOps manifests
├── monitoring/              # Prometheus + Grafana
└── .github/workflows/       # GitHub Actions CI/CD

## 🔧 Run Locally
```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

## 🐳 Docker
```bash
docker build -t home-essentials .
docker run -p 8000:8000 home-essentials
```

## ☸️ Deploy to Kubernetes
```bash
aws eks update-kubeconfig --name home-essentials-eks --region us-east-1
helm upgrade --install home-essentials ./helm
kubectl get pods
kubectl get svc
```

## 🏗 Infrastructure
```bash
cd terraform-local
terraform init
terraform plan
terraform apply
```

## 👨‍💻 Author
Masterpiece — Cloud Engineering Student
