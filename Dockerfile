FROM ghcr.io/astral-sh/uv:bookworm-slim

WORKDIR /app
VOLUME /data

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN uv python install 3.12

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

RUN apt update && \
    apt install --no-install-recommends -y \
    libgl1 \
    libegl1 \
    libglx-mesa0  \
    fontconfig \
    gettext \
    ca-certificates \
    fonts-noto-color-emoji && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    apt-get clean all

ENV LOAD_BUILTIN_MEMES=true \
    MEME_DIRS="[\"/data/memes\"]" \
    MEME_DISABLED_LIST="[]" \
    GIF_MAX_SIZE=10.0 \
    GIF_MAX_FRAMES=100 \
    LOG_LEVEL="INFO" \
    HOST="0.0.0.0" \
    PORT="2233"

ENV PATH="/app/.venv/bin:$PATH"

COPY ./meme_generator /app/meme_generator
COPY ./resources/fonts/* /usr/share/fonts/meme/
COPY ./pyproject.toml /app/pyproject.toml
COPY ./README.md /app/README.md
COPY ./docker/start.sh /app/start.sh
COPY ./docker/config.toml.template /app/config.toml.template
COPY ./uv.lock /app/uv.lock

RUN fc-cache -fv && \
    rm -f /usr/share/fontconfig/conf.avail/05-reset-dirs-sample.conf && \
    mkdir -p ~/.config/meme_generator && \
    chmod +x /app/start.sh

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

#  测试运行
RUN uv run meme

CMD ["sh", "/app/start.sh"]
