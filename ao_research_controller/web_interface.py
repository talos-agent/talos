#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask front‑end para iniciar o experimento AO Research Controller
e publicar os resultados no IPFS.
"""

import json
import logging
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

import ipfshttpclient

from ao_controller import TrialConfig, run_trial, TrialResult

# --------------------------------------------------------------------------- #
# Config Flask
# --------------------------------------------------------------------------- #
app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)   # silencia logs de request

# --------------------------------------------------------------------------- #
# IPFS – cliente local (é preciso ter o daemon rodando)
# --------------------------------------------------------------------------- #
def ipfs_client():
    return ipfshttpclient.connect()   # assume /ip4/127.0.0.1/tcp/5001

# --------------------------------------------------------------------------- #
# Rotas
# --------------------------------------------------------------------------- #
@app.route("/")
def index():
    return """
    <h2>AO Research Controller – Interface de Experimento</h2>
    <p>
        <a href="/run?verbose=0">Iniciar experimento padrão</a><br/>
        <a href="/run?verbose=1">Iniciar experimento (modo verboso)</a>
    </p>
    """


@app.route("/run")
def run():
    """Inicia a simulação, faz upload ao IPFS e devolve o CID."""
    verbose = request.args.get("verbose", "0") == "1"

    # Monta configuração (pode ser parametrizada via query‑string se quiser)
    cfg = TrialConfig(verbose=verbose)

    # Executa experimento
    result: TrialResult = run_trial(cfg)

    # Upload para IPFS (CSV + JSON)
    client = ipfs_client()
    out_dir = cfg.out_dir
    files_to_add = [str(out_dir / "trial_data.csv"), str(out_dir / "metadata.json")]
    res = client.add(files_to_add, pin=True, wrap_with_directory=True)

    # O último item da lista é a pasta “wrapped”; seu hash é o CID do dataset
    dataset_cid = res[-1]["Hash"]
    result.ipfs_cid = dataset_cid

    # Log resumido
    app.logger.info(f"Upload concluído – CID: {dataset_cid}")

    payload = {
        "status": "completed",
        "cid": dataset_cid,
        "gateway_url": f"https://ipfs.io/ipfs/{dataset_cid}",
        "config": result.config,
    }
    return jsonify(payload)


@app.route("/download/<path:filename>")
def download(filename):
    """Serviço opcional de download local (útil para debugging)."""
    directory = Path("./results")
    return send_from_directory(directory, filename, as_attachment=True)


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Avisos iniciais
    if not os.system("pgrep -x ipfs > /dev/null"):
        app.run(host="0.0.0.0", port=5000, debug=False)
    else:
        print(
            "❗  O daemon do IPFS não está ativo. "
            "Instale o IPFS (https://docs.ipfs.io/install/command-line/) "
            "e execute `ipfs daemon` antes de iniciar a interface."
        )