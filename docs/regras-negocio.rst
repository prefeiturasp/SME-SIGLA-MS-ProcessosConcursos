Regras de negócio
=================

Esta seção descreve as **regras que o sistema aplica** — ou seja, o que pode e o que não pode acontecer no cadastro de concursos, cargos e autorizações.

Concurso
--------

O que é
~~~~~~~

Um **concurso** representa um edital/processo seletivo da SME. Cada concurso guarda:

- Nome do concurso
- Número do processo administrativo
- Código do concurso na SME (quando importado da integração)
- Ano do edital
- Banca responsável
- Status (**Ativo** ou **Inativo**)
- Lista de **cargos** vinculados

Status do concurso
~~~~~~~~~~~~~~~~~~

.. list-table:: Status do concurso
   :header-rows: 1
   :widths: 25 75

   * - Status
     - Significado
   * - **Ativo**
     - Concurso disponível para uso e consulta (padrão ao criar)
   * - **Inativo**
     - Concurso marcado como inativo; permanece no banco e pode ser filtrado

O status **não bloqueia automaticamente** cargos nem autorizações. Ele serve principalmente para organização na tela e filtros de listagem.

Regras importantes sobre concurso
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- O **nome** é obrigatório (até 200 caracteres).
- O **número do processo** é obrigatório na API e **não pode ser vazio**.
- Dois concursos **não podem ter o mesmo número de processo** (quando preenchido).
- Mensagem em caso de duplicidade: *"Este número de processo já está cadastrado."*
- Os cargos são vinculados por lista de identificadores (``cargos_ids``):

  - Identificadores inexistentes são **ignorados** (só vincula os que existem).
  - Lista vazia **remove** todos os vínculos de cargo daquele concurso.
- Excluir um concurso **não apaga** os cargos nem as autorizações — apenas o registro do concurso e seus vínculos.

Cargos
------

O que é
~~~~~~~

Um **cargo** é a função/posição ofertada nos concursos (ex.: Professor de Educação Básica I). Cada cargo guarda:

- Nome
- **Código** numérico usado pela SME (chave da integração)

O mesmo cargo pode participar de **vários concursos** (relação muitos-para-muitos).

Regras de cargos
~~~~~~~~~~~~~~~~

- Nome é obrigatório (até 200 caracteres).
- Na importação da SME Integração, o sistema faz **upsert** pelo código: se o cargo já existe, atualiza o nome quando necessário; se não existe, cria.
- Um cargo que **já possui autorizações publicadas** **não pode ser excluído** (o sistema protege o histórico).
- A listagem de cargos na API **não é paginada** — retorna o conjunto completo (adequado a selects e painéis).

Autorizações publicadas
-----------------------

O que é
~~~~~~~

Uma **autorização publicada** registra quantas autorizações (vagas) foram publicadas para um **cargo** em uma **data**, com observação opcional.

Cada registro guarda:

- Cargo vinculado (pode ficar sem cargo em casos legados)
- Quantidade de autorizações
- Data da autorização
- Observação (texto livre)

Regras importantes
~~~~~~~~~~~~~~~~~~

- O cargo, quando informado, precisa existir — caso contrário a API rejeita a operação.
- Registros **sem data de autorização** entram no cadastro, mas são **excluídos das agregações e da extração de dados**.
- Registros **sem cargo** entram no **total geral** de autorizações, mas **não aparecem** na lista de cargos do relatório.
- Excluir um cargo com autorizações vinculadas é **bloqueado** para preservar o histórico.

Extração de dados
-----------------

A **extração de dados** monta um resumo de autorizações para relatórios e painéis.

Como funciona
~~~~~~~~~~~~~

1. O usuário (ou o frontend) informa, opcionalmente:

   - Um **concurso** (``concurso_uuid``)
   - Uma lista de **anos** (ex.: 2025 e 2026)

2. O sistema considera apenas autorizações **com data preenchida**.
3. Se um concurso for informado, considera **somente os cargos vinculados** àquele concurso.
4. Se anos forem informados, o resultado vem **separado por ano**, com:

   - Total de autorizações publicadas no ano
   - Lista de cargos com soma de autorizações e data mais recente daquele ano

5. Sem anos, o resultado é um único bloco com o total geral e a lista de cargos.

Assim a equipe consegue responder perguntas como: *"Quantas autorizações o Concurso 2026 já publicou no ano corrente, por cargo?"*

Comparação com escolhas
-----------------------

Há um endpoint que, por cargo, mostra:

- Total de **autorizações publicadas** (soma local)
- Data da **última** autorização
- Total de **escolhas** já registradas no **Módulo Escolhas** (por código do cargo)

Isso permite comparar *o que foi autorizado* com *o que já foi escolhido*, sem misturar as duas fontes de verdade.

Importação da SME Integração
----------------------------

O comando de importação (``criar_concursos_api``) segue estas regras:

1. Busca a lista oficial de **cargos** e faz upsert pelo código.
2. Busca os **tipos de concurso** e faz upsert pelo código do concurso.
3. Atualiza nome e número de processo quando necessário.
4. Vincula os cargos ao concurso pelos códigos retornados pela API.
5. Pode ser executado em modo **dry-run** (simulação sem gravar).

Se a URL ou o token da SME Integração não estiverem configurados, a importação **falha com erro claro** — não grava dados parciais silenciosos.

Auditoria
---------

Alterações em concursos, cargos e autorizações publicadas são **registradas automaticamente** (quem alterou, quando e o que mudou). Isso garante rastreabilidade para auditorias e consultas futuras.
