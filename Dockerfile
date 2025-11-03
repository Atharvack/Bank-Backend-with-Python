FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /code

# Install dependencies
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./app /code/app


RUN ruff check /code/app --fix




EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
