# Relatório de Estoque - API FastAPI

Este projeto é um serviço backend que gera relatórios do estoque com dados obtidos de uma API externa de produtos. Os relatórios podem ser consultados em formato JSON, Excel e PDF.

---

## Endpoints

### 1. `GET /relatorio/estoque`

Retorna a lista dos produtos em formato JSON com os seguintes campos:

- `nome`: Nome do produto
- `quantidade`: Quantidade disponível no estoque

**Exemplo de resposta:**

```json
[
  {
    "nome": "Produto A",
    "quantidade": 10
  },
  {
    "nome": "Produto B",
    "quantidade": 5
  }
]
