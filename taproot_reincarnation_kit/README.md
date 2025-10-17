# Taproot Reincarnation Kit

Esta é uma ferramenta de linha de comando (CLI) para demonstrar a criação de um endereço Bitcoin Taproot (P2TR) com uma condição de gasto baseada em um script leaf. Especificamente, ela cria um endereço que só pode ser gasto se a transação incluir uma assinatura válida e uma mensagem secreta específica.

O conceito, "reencarnação on-chain", é uma forma poética de descrever como uma identidade (representada por uma chave privada) pode se manifestar na blockchain através da revelação de uma mensagem secreta.

## Conceito

O endereço Taproot gerado tem duas condições de gasto (paths):

1.  **Key Path (Caminho da Chave):** O gasto padrão, usando a chave de saída Taproot. Este script não foca neste caminho.
2.  **Script Path (Caminho do Script):** Um caminho de gasto alternativo que requer a revelação de um script. Neste caso, o script exige:
    -   Uma assinatura válida da chave interna (a "alma").
    -   A revelação da mensagem secreta (ex: "Eu reencarnei na blockchain").

Este kit gera todos os componentes necessários para criar e (teoricamente) gastar de tal endereço.

## Instalação

### Pré-requisitos
- Python 3.8 ou superior

### Passos

1.  **Clone o repositório (ou tenha acesso a esta pasta):**
    ```bash
    # Exemplo, se o projeto estivesse em um repositório git
    # git clone https://github.com/your-username/taproot-reincarnation-kit.git
    # cd taproot-reincarnation-kit
    ```

2.  **Instale o pacote em modo editável:**
    ```bash
    pip install -e .
    ```
    Isso instalará a dependência (`ecdsa`) e criará o comando `reincarnate-cli` no seu ambiente.

## Uso

Após a instalação, você pode usar a ferramenta `reincarnate-cli` no seu terminal.

### Gerar um Novo Endereço com uma Nova Chave

Simplesmente execute o comando sem argumentos para gerar uma nova chave secreta e o endereço correspondente com a mensagem padrão:
```bash
reincarnate-cli
```

### Usar uma Chave Secreta Específica

Você pode fornecer sua própria chave secreta de 32 bytes em formato hexadecimal:
```bash
reincarnate-cli --secret-key sua_chave_secreta_hex
```

### Usar uma Mensagem Customizada

Você pode especificar a mensagem secreta que será usada no script leaf:
```bash
reincarnate-cli --message "Minha mensagem secreta aqui"
```

### Combinar Opções

```bash
reincarnate-cli --secret-key sua_chave_secreta_hex --message "Outra mensagem"
```

## Saída do Script

A ferramenta irá imprimir no console:
- A chave secreta (se gerada) e a chave pública interna.
- O hash da mensagem secreta.
- O script leaf em hexadecimal.
- O hash do TapLeaf.
- O tweak Taproot.
- A chave de saída Taproot.
- O endereço final `bc1p...` (bech32m).
- Um exemplo do *witness* necessário para gastar os fundos, que inclui a assinatura (de uma transação dummy), a mensagem, o script e o control block.

**AVISO DE SEGURANÇA:** Este script é para fins educacionais. Não use as chaves geradas ou os endereços em um ambiente de produção com fundos reais sem um entendimento completo das implicações de segurança do Taproot e do Bitcoin.