FROM ghcr.io/astral-sh/uv:0.6.1-python3.12-bookworm-slim

LABEL org.opencontainers.image.source=https://github.com/siemdejong/ithappens

WORKDIR /app

ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --compile-bytecode --no-editable

EXPOSE 8501
ENTRYPOINT ["uv", "run", "streamlit", "run", "src/app/main.py"]
CMD ["--server.port", "8501"]
