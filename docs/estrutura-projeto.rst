Estrutura do projeto
====================

Esta seção explica **cada pasta do repositório** e o papel de cada módulo dentro de ``apps/``.

Visão da árvore principal
-------------------------

.. code-block:: text

   ms-processos-concursos/
   ├── apps/              # Módulos de negócio (Django apps)
   ├── config/            # Configurações do projeto Django
   ├── docs/              # Documentação Sphinx (este material)
   ├── requirements/      # Dependências Python por ambiente
   ├── manage.py          # Ponto de entrada do Django
   ├── Dockerfile         # Imagem Docker da API
   ├── docker-compose.yml # Ambiente local (API + banco)
   └── Makefile           # Comandos úteis de desenvolvimento

Pasta ``apps/``
---------------

É onde ficam os **módulos de negócio**. Cada subpasta é um "app" Django com responsabilidade bem definida.

``apps/core/``
~~~~~~~~~~~~~~

**O que faz:** Fornece a base comum usada por todos os outros apps.

**Para que serve:** Evita repetir código. Todo modelo do sistema herda de ``BaseModel``, que já traz:

- Identificador único (UUID)
- Data de criação
- Data da última atualização
- Campo de histórico de auditoria

Também disponibiliza a paginação padrão das listagens da API (formato SIGLA com ``links``, ``count``, ``page``, ``page_size`` e ``results``).

**Analogia:** É a "ficha padrão" que todo cadastro do sistema usa — como um formulário com campos obrigatórios no topo.

``apps/concursos/``
~~~~~~~~~~~~~~~~~~~

**O que faz:** É o **coração** do microserviço. Gerencia o ciclo de vida dos concursos e concentra as migrations principais do domínio.

**Para que serve:**

- Criar, listar, editar e excluir concursos
- Vincular cargos a cada concurso
- Filtrar por nome, processo, ano, banca, status e cargo
- Expor listagem em formato ``select`` para componentes do frontend
- Importar concursos e cargos da API SME Integração

**Principais partes internas:**

.. list-table:: Módulos do app concursos
   :header-rows: 1
   :widths: 35 65

   * - Subpasta / arquivo
     - Função
   * - ``models.py``
     - Define o modelo ``Concurso``
   * - ``api/views.py``
     - Endpoints REST (CRUD e listagem)
   * - ``services/``
     - Regras de listagem e integração com SME
   * - ``repository.py``
     - Acesso ao banco de dados (consultas e persistência)
   * - ``serializers.py``
     - Validação e conversão dos dados da API
   * - ``filters.py``
     - Filtros de listagem
   * - ``constants.py``
     - Status do concurso (Ativo / Inativo)
   * - ``management/commands/``
     - Comandos de apoio (importar, criar exemplos, limpar)
   * - ``tests/``
     - Testes automatizados do app

**Exemplo:** Quando o analista abre um select de concursos no frontend, a API pode responder em ``?formato=select`` com ``value``, ``label`` e cargos já vinculados.

``apps/cargos/``
~~~~~~~~~~~~~~~~

**O que faz:** Gerencia o cadastro de **cargos** e a visão agregada de autorizações + escolhas.

**Para que serve:**

- Criar, listar, editar e excluir cargos
- Manter o código SME usado na integração
- Montar o resumo de autorizações publicadas por cargo
- Consultar o total de escolhas no Módulo Escolhas

**Principais partes internas:**

.. list-table:: Módulos do app cargos
   :header-rows: 1
   :widths: 35 65

   * - Subpasta / arquivo
     - Função
   * - ``models.py``
     - Modelo ``Cargo``
   * - ``services/``
     - Agregação de autorizações e cliente HTTP do Módulo Escolhas
   * - ``api/views.py``
     - Endpoints REST de cargos e resumo
   * - ``repository.py``
     - Consultas e persistência no banco
   * - ``serializers.py``
     - Validação e conversão dos dados da API

**Exemplo:** O painel solicita ``GET /cargos/autorizacoes-publicadas/`` e recebe, por cargo, o total autorizado localmente e o total de escolhas vindas do Módulo Escolhas.

``apps/autorizacoes/``
~~~~~~~~~~~~~~~~~~~~~~

**O que faz:** Cuida das **autorizações publicadas** e da **extração de dados** para relatórios.

**Para que serve:**

- Registrar quantidades de autorizações por cargo e data
- Listar e editar esses registros
- Montar extrações filtradas por concurso e/ou anos

**Principais partes internas:**

.. list-table:: Módulos do app autorizacoes
   :header-rows: 1
   :widths: 35 65

   * - Subpasta / arquivo
     - Função
   * - ``models.py``
     - Modelo ``AutorizacaoPublicada``
   * - ``services/``
     - Montagem da extração de dados
   * - ``api/views.py``
     - Endpoints de CRUD e extração
   * - ``repository.py``
     - Consultas, agregações e persistência
   * - ``serializers.py``
     - Validação e conversão dos dados da API

**Exemplo:** O frontend envia ``POST /extracao-dados/`` com o UUID do concurso e os anos desejados; o app devolve totais e a lista de cargos daquele recorte.

Pasta ``config/``
-----------------

**O que faz:** Configurações centrais do projeto Django.

**Para que serve:**

.. list-table:: Arquivos de configuração
   :header-rows: 1
   :widths: 25 75

   * - Arquivo
     - Função
   * - ``settings.py``
     - Banco de dados, apps instalados, CORS, URLs de integração, idioma e fuso horário
   * - ``settings_test.py``
     - Configuração usada pelos testes automatizados
   * - ``urls.py``
     - Rotas da API (``/api/v1/``), admin, healthcheck e Swagger
   * - ``wsgi.py``
     - Ponto de entrada para servidores de produção

**Exemplo:** As variáveis ``SMEINTEGRACAO_API_URL`` e ``ESCOLHAS_API_URL`` em ``settings.py`` dizem ao sistema onde buscar cargos/concursos oficiais e totais de escolhas.

Pasta ``requirements/``
-----------------------

**O que faz:** Lista as **dependências Python** do projeto, separadas por ambiente.

**Para que serve:**

.. list-table:: Arquivos de dependências
   :header-rows: 1
   :widths: 25 75

   * - Arquivo
     - Conteúdo
   * - ``base.txt``
     - Dependências essenciais (Django, DRF, PostgreSQL, auditlog)
   * - ``local.txt``
     - Desenvolvimento (testes, lint, Sphinx, debug toolbar)
   * - ``production.txt``
     - Produção (gunicorn)

Pasta ``docs/``
---------------

**O que faz:** Contém esta documentação em formato reStructuredText (``.rst``) e a configuração do Sphinx.

**Para que serve:** Gerar o site HTML de documentação com ``make docs`` ou ``sphinx-build``.

Arquivos na raiz
----------------

.. list-table:: Arquivos na raiz do projeto
   :header-rows: 1
   :widths: 25 75

   * - Arquivo
     - Função
   * - ``manage.py``
     - Comando Django (migrações, servidor, superusuário, importações)
   * - ``docker-compose.yml``
     - Sobe API e PostgreSQL juntos
   * - ``Dockerfile``
     - Constrói a imagem Docker da API
   * - ``Makefile``
     - Atalhos: testes, lint, migrações e documentação
   * - ``README.md``
     - Visão técnica rápida e instruções de execução
   * - ``env.example``
     - Modelo de variáveis de ambiente necessárias

API — endpoints principais (referência)
---------------------------------------

Para consulta rápida, os principais caminhos da API (prefixo ``/api/v1/``):

**Concursos**

- ``GET /concursos/`` — Listar concursos (paginado; use ``?formato=select`` para selects)
- ``POST /concursos/`` — Criar concurso
- ``GET /concursos/{uuid}/`` — Detalhes
- ``PUT /concursos/{uuid}/`` — Atualizar completo
- ``PATCH /concursos/{uuid}/`` — Atualizar parcial
- ``DELETE /concursos/{uuid}/`` — Remover

**Cargos**

- ``GET /cargos/`` — Listar cargos
- ``POST /cargos/`` — Criar cargo
- ``GET /cargos/{uuid}/`` — Detalhes
- ``PUT /cargos/{uuid}/`` — Atualizar completo
- ``PATCH /cargos/{uuid}/`` — Atualizar parcial
- ``DELETE /cargos/{uuid}/`` — Remover (quando permitido)
- ``GET /cargos/autorizacoes-publicadas/`` — Resumo de autorizações + escolhas por cargo

**Autorizações publicadas**

- ``GET /autorizacoes-publicadas/`` — Listar
- ``POST /autorizacoes-publicadas/`` — Criar
- ``GET /autorizacoes-publicadas/{uuid}/`` — Detalhes
- ``PUT /autorizacoes-publicadas/{uuid}/`` — Atualizar completo
- ``PATCH /autorizacoes-publicadas/{uuid}/`` — Atualizar parcial
- ``DELETE /autorizacoes-publicadas/{uuid}/`` — Remover
- ``POST /extracao-dados/`` — Extração agregada por concurso e/ou anos

A documentação interativa da API (Swagger) está disponível em ``/api/docs/`` quando o servidor está rodando.

Comandos úteis de management
----------------------------

.. list-table:: Comandos Django
   :header-rows: 1
   :widths: 40 60

   * - Comando
     - Finalidade
   * - ``criar_concursos_api``
     - Importa cargos e concursos da SME Integração (aceita ``--dry-run``)
   * - ``criar_concursos``
     - Gera concursos de exemplo para desenvolvimento
   * - ``limpar_concursos``
     - Remove concursos e cargos (uso em ambiente de desenvolvimento)
