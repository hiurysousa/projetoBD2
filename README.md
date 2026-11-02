# Projeto BD II — Concorrência em uma concessionária

API educacional desenvolvida para a disciplina de Banco de Dados II. O projeto
simula dois vendedores tentando vender o mesmo veículo ao mesmo tempo e mostra
como uma transação pode impedir a duplicidade da venda.

> **Nota sobre a tecnologia:** embora a ideia inicial possa ter considerado
> MongoDB, a implementação disponível neste repositório usa **SQLite**. A API é
> construída com **FastAPI** e a simulação abre transações explícitas com
> `BEGIN IMMEDIATE`.

## Objetivo

O cenário parte de uma concessionária com veículos disponíveis para venda. Duas
threads representam vendedores concorrentes e tentam registrar a venda do
veículo de ID `101`. A primeira transação obtém um bloqueio de escrita; a outra
precisa aguardar ou falha pelo tempo limite. Ao final, apenas uma venda deve ser
registrada.

O exemplo ajuda a observar, de forma simplificada:

- atomicidade da atualização do veículo e do registro da venda;
- isolamento entre operações concorrentes;
- bloqueio de escrita do SQLite;
- `COMMIT` em caso de sucesso e descarte da operação em caso de erro.

## Tecnologias

- Python 3.13
- FastAPI
- SQLite (`sqlite3` da biblioteca padrão)
- Poetry
- Pytest, Ruff, SQLAlchemy e Alembic (estrutura complementar/legada)

## Estrutura do projeto

```text
.
├── fast_zero/
│   ├── app.py              # API e simulação de venda concorrente
│   ├── database_setup.py   # versão executável da simulação no terminal
│   ├── database.py         # configuração SQLAlchemy complementar
│   ├── models.py           # modelo de usuário da estrutura anterior
│   ├── schemas.py          # schemas Pydantic da estrutura anterior
│   └── settings.py         # leitura de variáveis de ambiente
├── migrations/             # configuração do Alembic
├── tests/                  # testes da estrutura CRUD anterior
├── .env.example            # exemplo seguro de configuração local
├── pyproject.toml          # dependências e comandos do projeto
└── poetry.lock             # versões reproduzíveis das dependências
```

## Como executar

### 1. Pré-requisitos

- [Python 3.13](https://www.python.org/downloads/)
- [Poetry 2](https://python-poetry.org/docs/#installation)

### 2. Instalação

```bash
git clone https://github.com/hiurysousa/projetoBD2.git
cd projetoBD2
poetry install
```

O `.env` não é necessário para a simulação principal. Caso você trabalhe com a
camada SQLAlchemy complementar, crie a configuração local a partir do exemplo:

```bash
cp .env.example .env
```

No PowerShell, use `Copy-Item .env.example .env`.

### 3. Inicialização da API

```bash
poetry run task run
```

A API ficará disponível em `http://127.0.0.1:8000`. A documentação interativa
gerada pelo FastAPI pode ser acessada em:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Fluxo da demonstração

Com a aplicação em execução, use a Swagger UI ou os comandos abaixo.

### 1. Criar e popular o banco local

```bash
curl -X POST http://127.0.0.1:8000/init-db
```

Essa operação recria os dados da demonstração e insere os veículos de IDs `101`
e `200` como disponíveis.

### 2. Simular duas vendas concorrentes

```bash
curl -X POST http://127.0.0.1:8000/simulate-concurrent-sale
```

A requisição inicia duas threads que disputam o veículo `101`. O terminal da API
mostra qual transação concluiu e qual foi impedida pelo bloqueio ou pela mudança
de disponibilidade.

### 3. Conferir o resultado

```bash
curl http://127.0.0.1:8000/veiculos
curl http://127.0.0.1:8000/vendas
```

Resultado esperado: o veículo `101` fica com status `Vendido` e existe somente
um registro de venda para ele.

## Endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/init-db` | Cria as tabelas e restaura os dados da demonstração |
| `POST` | `/simulate-concurrent-sale` | Executa duas tentativas simultâneas de venda |
| `GET` | `/veiculos` | Lista os veículos e seus estados atuais |
| `GET` | `/vendas` | Lista as vendas registradas |

## Qualidade e testes

```bash
poetry run task lint
poetry run task format
poetry run task test
```

Os testes presentes foram escritos para uma versão anterior da API, baseada em
CRUD de usuários com SQLAlchemy, e ainda precisam ser atualizados para os
endpoints atuais da concessionária. Essa limitação é mantida explícita para não
dar a impressão de que a suíte valida a simulação atual.

## Segurança e arquivos locais

O repositório não deve versionar:

- arquivos `.env` com configurações locais;
- bancos SQLite (`*.db`, `*.sqlite` e `*.sqlite3`);
- caches, cobertura de testes e bytecode Python;
- configurações pessoais de IDE.

Esses itens estão cobertos pelo `.gitignore`. Use `.env.example` apenas como
modelo e nunca inclua credenciais reais nele.

## Possíveis evoluções

- atualizar os testes para o cenário de vendas concorrentes;
- separar acesso ao banco, regras de negócio e rotas da API;
- retornar modelos Pydantic em vez de tuplas do SQLite;
- adicionar chaves estrangeiras e restrições de integridade ao esquema;
- substituir `print` por logging estruturado;
- comparar o controle de concorrência do SQLite com PostgreSQL ou MongoDB.

## Autor

Desenvolvido por [Hiury Sousa](https://github.com/hiurysousa) como projeto
acadêmico de Banco de Dados II.
