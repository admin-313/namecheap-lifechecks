FROM python:3.13-slim

WORKDIR /opt/lifechecker

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"

COPY . .
RUN uv pip install --system .
# So logs appear instantly in docker logs
ENV PYTHONUNBUFFERED=1

CMD ["python3", "src/namecheap_lifechecks/main.py"]
