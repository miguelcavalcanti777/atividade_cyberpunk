# Roteiro: SQLite -> PostgreSQL do servidor (Atividade 2)

Ordem importa: o banco novo nasce vazio, então os dados antigos precisam ser
exportados ANTES de trocar o banco no `.env`.

## 0. Pré-requisito
O `db.sqlite3` com os dados antigos precisa estar na pasta do projeto
(o arquivo NÃO vai para o Git; está no .gitignore).

## 1. Exportar do SQLite (ainda com DB_ENGINE=sqlite ou sem .env de banco)
    python manage.py dumpdata cyberpunk auth.user --natural-foreign --natural-primary --indent 2 -o dados.json
(Se der erro de encoding no Windows: `python -X utf8 manage.py dumpdata ...`)

## 2. Trocar para o PostgreSQL
Crie o `.env` (copie de `.env.example`) com DB_ENGINE=postgresql, equipeNN, senha, host.
Confirme que `.env` está no `.gitignore`.

## 3. Criar as tabelas no servidor
    python manage.py migrate
(A tabela `modalidade` NÃO é criada: o model é managed = False e ela já existe.)

## 4. Importar os dados
    python manage.py loaddata dados.json
Se reclamar de contenttypes/permissions já existentes, refaça o passo 1 sem
`auth.user` e crie o usuário no passo 5.

## 5. Superusuário novo
    python manage.py createsuperuser

## 6. Renomear (não apagar) o SQLite
    ren db.sqlite3 db.sqlite3.bak        (Windows)   |   mv db.sqlite3 db.sqlite3.bak   (Linux/Mac)

## 7. Provar
    python manage.py runserver
- /admin/ entra com o superusuário novo
- /contratos/, /personagens/ e /modalidades/ listam dados do servidor
- SQLTools: tabelas cyberpunk_* aparecem no banco equipeNN (print para o documento)

## 8. Commit
    git add .
    git commit -m "banco: PostgreSQL"
    git push
(Confira com `git status` que .env e db.sqlite3* NÃO aparecem.)

## Sem o SQLite antigo?
Se o db.sqlite3 se perdeu, `python manage.py popular_dados` cria dados de
exemplo, mas isso NÃO prova a migração dos dados antigos (requisito 4).
