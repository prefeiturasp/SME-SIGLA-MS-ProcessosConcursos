# Changelog - Renomeação de Processos para Concursos

## 📝 Resumo das Alterações

Este documento descreve todas as alterações realizadas para renomear o projeto de "Processos de Convocação" para "Concursos".

## 🔄 Alterações nos Modelos

### models.py
- ✅ Renomeado `ProcessoConvocacao` para `Concurso`
- ✅ Renomeado `PROCESSO_STATUS_CHOICES` para `CONCURSO_STATUS_CHOICES`
- ✅ Renomeado `PROCESSO_TIPOS_CHOICES` para `CONCURSO_TIPOS_CHOICES`
- ✅ Renomeado campo `tipo_processo` para `tipo_concurso`
- ✅ Atualizado `verbose_name` de "Processo de Convocação" para "Concurso"
- ✅ Atualizado `db_table` de `processos_convocacao` para `concursos`
- ✅ Corrigido `numero_convocados` (era `numero_convocacao`)

### Migrações
- ✅ Atualizado `0001_initial.py` com novo nome do modelo
- ✅ Criado `0002_rename_tipo_processo_to_tipo_concurso.py` para renomear campo
- ✅ Criado `0003_rename_table.py` para renomear tabela

## 🔄 Alterações nas Views

### views.py
- ✅ Renomeado `ProcessoConvocacaoViewSet` para `ConcursoViewSet`
- ✅ Atualizado `filterset_fields` de `tipo_processo` para `tipo_concurso`
- ✅ Atualizado todas as referências de `processo` para `concurso`
- ✅ Atualizado mensagens de erro e comentários

## 🔄 Alterações nos Serializers

### serializers.py
- ✅ Renomeado `ProcessoConvocacaoSerializer` para `ConcursoSerializer`
- ✅ Atualizado referência do modelo

## 🔄 Alterações no Admin

### admin.py
- ✅ Renomeado `ProcessoConvocacaoAdmin` para `ConcursoAdmin`
- ✅ Atualizado docstring e comentários

## 🔄 Alterações nas URLs

### urls.py
- ✅ Atualizado rota de `processos-convocacao` para `concursos`
- ✅ Atualizado import da view

## 🔄 Alterações na Configuração

### apps.py
- ✅ Renomeado `ProcessosConfig` para `ConcursosConfig`
- ✅ Atualizado `name` de `processos` para `concursos`

### settings.py
- ✅ Atualizado `INSTALLED_APPS` de `processos` para `concursos`
- ✅ Atualizado `DB_NAME` padrão de `processos_convocacao` para `concursos`

### config/urls.py
- ✅ Atualizado include de `processos.urls` para `concursos.urls`

## 🔄 Alterações nos Comandos Customizados

### management/commands/
- ✅ Renomeado `criar_processos.py` para `criar_concursos.py`
- ✅ Renomeado `limpar_processos.py` para `limpar_concursos.py`
- ✅ Atualizado todas as referências de modelos e campos
- ✅ Atualizado mensagens e help text

## 🔄 Alterações na Documentação

### README.md
- ✅ Atualizado título do projeto
- ✅ Atualizado estrutura de diretórios
- ✅ Atualizado endpoints da API
- ✅ Atualizado comandos customizados
- ✅ Atualizado modelo de dados
- ✅ Atualizado configurações de banco

### README_DOCKER.md
- ✅ Atualizado nome do banco de dados
- ✅ Atualizado comandos de conexão

### docker-compose.yml
- ✅ Atualizado nome do container
- ✅ Atualizado nome do banco de dados
- ✅ Atualizado nome da rede

### env.example
- ✅ Atualizado `DB_NAME` padrão

## 🔄 Alterações na Estrutura de Diretórios

- ✅ Renomeado pasta `processos/` para `concursos/`
- ✅ Mantida estrutura interna dos arquivos

## 🚀 Como Aplicar as Alterações

### 1. Parar o servidor Django (se estiver rodando)

### 2. Aplicar as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Verificar se tudo está funcionando
```bash
python manage.py runserver
```

### 4. Testar a API
- Acesse: http://localhost:8000/api/v1/concursos/
- Verifique se os endpoints estão funcionando

### 5. Testar comandos customizados
```bash
python manage.py criar_concursos
python manage.py limpar_concursos
```

## ⚠️ Observações Importantes

1. **Backup**: Faça backup do banco antes de aplicar as migrações
2. **Dependências**: Verifique se não há outros arquivos que referenciem os nomes antigos
3. **Testes**: Execute os testes para garantir que tudo está funcionando
4. **Frontend**: Atualize o frontend para usar os novos endpoints

## 🔍 Verificações Pós-Migração

- [ ] API está respondendo em `/api/v1/concursos/`
- [ ] Admin Django está funcionando
- [ ] Comandos customizados estão funcionando
- [ ] Migrações foram aplicadas com sucesso
- [ ] Banco de dados foi renomeado corretamente

## 📞 Suporte

Em caso de problemas durante a migração, verifique:
1. Logs do Django
2. Logs do banco de dados
3. Status das migrações (`python manage.py showmigrations`)
4. Estrutura atual do banco 