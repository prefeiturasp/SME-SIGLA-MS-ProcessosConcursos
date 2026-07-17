Visão geral
===========

O que é este módulo?
--------------------

O **Módulo Processos de Concursos** é o sistema responsável por cadastrar e organizar os **concursos públicos** da SME (Secretaria Municipal de Educação de São Paulo), os **cargos** vinculados a cada edital e as **autorizações publicadas** (quantidades de vagas autorizadas ao longo do tempo).

Em termos simples: antes de convocar candidatos ou acompanhar escolhas de vaga, é preciso ter uma base confiável de *quais concursos existem*, *quais cargos cada um oferece* e *quantas autorizações já foram publicadas*. Este módulo cuida dessa base.

Para que serve?
---------------

O sistema permite que a equipe da SME:

- **Cadastre e consulte concursos** (nome, número de processo, ano do edital, banca e status)
- **Vincule cargos** a cada concurso (código e nome oficiais da SME)
- **Registre autorizações publicadas** por cargo e data
- **Extraia totais** de autorizações por concurso e por ano (relatórios e painéis)
- **Compare autorizações com escolhas** já realizadas (integração com o Módulo Escolhas)
- **Importe dados** da API SME Integração, evitando cadastro manual repetitivo

Onde ele se encaixa no ecossistema SIGLA?
-----------------------------------------

Este módulo **não trabalha sozinho**. Ele se integra com outros sistemas:

.. list-table:: Integrações do ecossistema
   :header-rows: 1
   :widths: 30 70

   * - Sistema
     - Papel no processo de concursos
   * - **API SME Integração**
     - Fonte oficial de cargos e tipos de concurso (importação em lote)
   * - **Módulo Escolhas**
     - Informa o total de escolhas por cargo, para comparação com autorizações
   * - **Módulo Processos de Convocação**
     - Consome os concursos cadastrados ao abrir um processo de convocação
   * - **Frontend SIGLA**
     - Interface usada pela equipe para consultar e operar o cadastro

O Módulo Processos de Concursos é a **referência central** de editais, cargos e autorizações usadas pelos demais fluxos do SIGLA.

Exemplo prático do dia a dia
----------------------------

Imagine o seguinte cenário:

1. A SME homologa o **Concurso Público 2026** para Professor de Educação Básica.
2. Um analista (ou um comando de importação) **cadastra o concurso** com número de processo, ano do edital e banca.
3. Os **cargos** do edital (ex.: Professor I, Professor II) são associados ao concurso.
4. Conforme saem publicações oficiais, a equipe **registra autorizações** — por exemplo, 50 vagas para o cargo X na data Y.
5. Em um painel ou relatório, o sistema **soma as autorizações** daquele concurso/ano e, se necessário, mostra também quantas **escolhas** já foram feitas no Módulo Escolhas.
6. Mais adiante, o Módulo de Convocação usa esse concurso como base para abrir um processo de convocação.

Fluxo resumido
--------------

.. code-block:: text

   Dados oficiais (SME Integração)  ----->  Importar / cadastrar cargos
                                                    |
                                                    v
                                           Cadastrar concurso
                                           e vincular cargos
                                                    |
                                                    v
                                           Registrar autorizações
                                           publicadas (por data)
                                                    |
                          +-------------------------+-------------------------+
                          |                                                   |
                          v                                                   v
               Extração / relatórios                              Comparar com escolhas
               (por concurso e ano)                               (Módulo Escolhas)
                          |
                          v
               Outros módulos SIGLA
               (ex.: convocação)

Tecnologias utilizadas (referência rápida)
------------------------------------------

Para quem precisa de contexto técnico sem entrar no código:

- **Django** — framework web que estrutura o projeto
- **Django REST Framework** — expõe a API consumida pelo frontend
- **PostgreSQL** — banco de dados onde ficam concursos, cargos e autorizações
- **django-auditlog** — registra quem alterou o quê e quando
- **drf-spectacular** — documentação interativa da API (Swagger)
