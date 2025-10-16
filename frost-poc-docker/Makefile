# --------------------------------------------------------------
# Makefile – pontos de entrada para o fluxo FROST
# --------------------------------------------------------------

# Variáveis
DOCKER_IMG   := frost-poc-docker:latest
DATA_DIR     := $(CURDIR)/data
SHARES_DIR   := $(DATA_DIR)/shares
PSBT_DIR     := $(DATA_DIR)/psbt
FINAL_TX     := $(DATA_DIR)/final.tx

# -----------------------------------------------------------------
# Build da imagem Docker (executa apenas uma vez)
# -----------------------------------------------------------------
docker-build:
	@docker build -t $(DOCKER_IMG) .

# -----------------------------------------------------------------
# Gera as shares (threshold = 3 de 5)
# -----------------------------------------------------------------
generate-shares:
	@docker run --rm -v $(SHARES_DIR):/data $(DOCKER_IMG) \
		generate-shares.sh 5 3 /data

# -----------------------------------------------------------------
# Cria o PSBT a partir das inputs fornecidos (arquivo inputs.json)
# -----------------------------------------------------------------
create-psbt:
	@docker run --rm -v $(PSBT_DIR):/data $(DOCKER_IMG) \
		create-psbt.sh /data/inputs.json /data/unsigned.psbt

# -----------------------------------------------------------------
# Assina o PSBT com as shares (executa 3 assinaturas aleatórias)
# -----------------------------------------------------------------
sign-frost:
	@docker run --rm -v $(PSBT_DIR):/data $(DOCKER_IMG) \
		sign-frost.sh /data/unsigned.psbt $(SHARES_DIR) /data/signed.psbt

# -----------------------------------------------------------------
# Finaliza o PSBT (combina as assinaturas e gera a transação final)
# -----------------------------------------------------------------
finalize:
	@docker run --rm -v $(PSBT_DIR):/data $(DOCKER_IMG) \
		finalize.sh /data/signed.psbt $(FINAL_TX)

# -----------------------------------------------------------------
# Verifica a transação final (hash, tamanho, taxa)
# -----------------------------------------------------------------
verify:
	@docker run --rm -v $(DATA_DIR):/data $(DOCKER_IMG) \
		verify.sh $(FINAL_TX)

# -----------------------------------------------------------------
# Limpa artefatos gerados
# -----------------------------------------------------------------
clean:
	rm -rf $(DATA_DIR)/*

.PHONY: docker-build generate-shares create-psbt sign-frost finalize verify clean