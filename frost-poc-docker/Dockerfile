# --------------------------------------------------------------
# Imagem base mínima com Rust (para FROST) e Bitcoin Core
# --------------------------------------------------------------
FROM ubuntu:22.04 AS builder

# ---- dependências de build ------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates curl git libssl-dev pkg-config \
    libsecp256k1-dev libsqlite3-dev libzmq3-dev \
    && rm -rf /var/lib/apt/lists/*

# ---- instalar Rust (toolchain estável) ------------------------------------
ENV RUSTUP_HOME=/opt/rustup \
    CARGO_HOME=/opt/cargo \
    PATH=/opt/cargo/bin:$PATH
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --no-modify-path \
    && rustup default stable

# ---- copiar código fonte ----------------------------------------------------
WORKDIR /app
COPY . /app

# ---- compilar binários FROST (exemplo genérico) ---------------------------
RUN cargo build --release

# --------------------------------------------------------------
# Imagem final (runtime only) – mínima e air‑gapped
# --------------------------------------------------------------
FROM ubuntu:22.04 AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 libsecp256k1-0 libsqlite3-0 libzmq5 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# copiar binários da fase builder
COPY --from=builder /app/target/release/frost-cli /usr/local/bin/frost-cli
COPY --from=builder /app/scripts/ /usr/local/bin/

# garantir permissões de execução
RUN chmod +x /usr/local/bin/*.sh

# diretório de trabalho (onde o usuário vai montar os dados)
WORKDIR /data
VOLUME ["/data"]
ENTRYPOINT ["/usr/local/bin/frost-cli"]