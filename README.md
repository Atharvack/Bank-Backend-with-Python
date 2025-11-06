# Backend

**Author:** Atharva Kulkarni  




## Requirements
- Docker installed



## Build Docker Image
```bash
docker build -t bank-api .
```

Run Container

```bash
docker run -d --name bank-container -p 8000:8000 bank-api
```
Access API
Open in browser or client:
http://localhost:8000

Fastapi Swagger UI:
http://localhost:8000/docs
