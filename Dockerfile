FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /code

# Install dependencies
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# --- Code Copying ---
# For Production, you would uncomment the line below to copy the code into the image.
# COPY ./app /code/app

# For Development, we don't copy the code here. Instead, we mount the local './app'
#directory as a volume in the `docker run` command. This enables hot reloading.


EXPOSE 8000

# --- Run Application ---
# The `--reload` flag enables hot reloading for development.
# For Production, you would remove the `--reload` flag.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
