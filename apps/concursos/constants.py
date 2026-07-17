"""Constantes do domínio de concursos."""

CONCURSO_STATUS_CHOICES = [
    ("ATIVO", "Ativo"),
    ("INATIVO", "Inativo"),
]

# Situação do ciclo de vida do concurso (distinta de ``status``).
# INCOMPLETO: cadastro iniciado (passo 1) e ainda não finalizado.
# COMPLETO: cadastro finalizado (último passo do wizard concluído).
# EM_ANDAMENTO: houve convocação; edição fica bloqueada. A transição para
#   este estado será feita pela integração de convocação (serviço
#   ``convocacao/``) — fora do escopo atual.
# FINALIZADO / CANCELADO: definidos para uso futuro (ainda não utilizados).
CONCURSO_SITUACAO_INCOMPLETO = "INCOMPLETO"
CONCURSO_SITUACAO_COMPLETO = "COMPLETO"
CONCURSO_SITUACAO_EM_ANDAMENTO = "EM_ANDAMENTO"
CONCURSO_SITUACAO_FINALIZADO = "FINALIZADO"
CONCURSO_SITUACAO_CANCELADO = "CANCELADO"

CONCURSO_SITUACAO_CHOICES = [
    (CONCURSO_SITUACAO_INCOMPLETO, "Incompleto"),
    (CONCURSO_SITUACAO_COMPLETO, "Completo"),
    (CONCURSO_SITUACAO_EM_ANDAMENTO, "Em andamento"),
    (CONCURSO_SITUACAO_FINALIZADO, "Finalizado"),
    (CONCURSO_SITUACAO_CANCELADO, "Cancelado"),
]
