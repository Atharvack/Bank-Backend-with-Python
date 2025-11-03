# Backend API

**Author:** Atharva Kulkarni  
**Submission:** Assessment Backend



## Requirements
- Docker installed



## Build Docker Image
```bash
docker build -t meow-api .
```

Run Container

```bash
docker run -d --name meow-container -p 8000:8000 meow-api
```
Access API
Open in browser or client:
http://localhost:8000

Fastapi Swagger UI:
http://localhost:8000/docs
