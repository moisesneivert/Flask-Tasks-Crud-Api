# Guia de instalação e atualização no GitHub

Este documento explica como abrir o projeto no Visual Studio Code, executar a API e substituir a versão atual do repositório sem perder o histórico do Git.

## 1. Preparar o repositório existente

No PowerShell, escolha uma pasta de trabalho e clone o repositório:

```powershell
cd C:\Users\DeLL\Documents\ROCKETSEAT\Python
git clone https://github.com/moisesneivert/Flask-Tasks-Crud-Api.git
cd Flask-Tasks-Crud-Api
code .
```

Se a pasta já estiver clonada, entre nela e confirme o estado atual:

```powershell
cd C:\caminho\para\Flask-Tasks-Crud-Api
git status
git branch --show-current
git remote -v
```

Antes de substituir os arquivos, salve qualquer alteração importante. Não apague a pasta oculta `.git`, pois ela contém o histórico e a ligação com o GitHub.

## 2. Copiar a nova versão

Extraia o arquivo fornecido e copie todo o conteúdo da pasta `flask-tasks-crud-api` para dentro da pasta clonada `Flask-Tasks-Crud-Api`.

Ao copiar:

- autorize a substituição dos arquivos existentes;
- mantenha a pasta `.git` do repositório clonado;
- remova do repositório qualquer pasta `__pycache__` antiga;
- não copie o ambiente de teste `.venv-test`, caso ele apareça em uma versão de validação local.

Depois, abra a pasta correta no VS Code:

```powershell
code .
```

## 3. Criar o ambiente virtual

No terminal integrado do VS Code:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Selecione o interpretador no VS Code:

1. Pressione `Ctrl + Shift + P`.
2. Procure por `Python: Select Interpreter`.
3. Selecione `.venv\Scripts\python.exe`.

## 4. Configurar e criar o banco

```powershell
Copy-Item .env.example .env
flask --app run.py db upgrade
flask --app run.py seed
```

O SQLite será criado em `instance\tasks.db`. Essa pasta não será enviada ao GitHub.

## 5. Executar a API

```powershell
python run.py
```

Acesse:

- API: `http://127.0.0.1:5000`
- Saúde: `http://127.0.0.1:5000/health`
- Tarefas: `http://127.0.0.1:5000/api/v1/tasks`

Também é possível pressionar `F5` e escolher `Flask API: debug`.

## 6. Executar os testes e a análise de código

```powershell
ruff check .
ruff format --check .
pytest
```

Resultado esperado desta versão:

```text
15 passed
Coverage total: aproximadamente 90%
```

Para corrigir automaticamente formatação e imports:

```powershell
ruff check . --fix
ruff format .
```

Execute novamente os testes depois de qualquer correção automática.

## 7. Conferir as mudanças do Git

```powershell
git status
git diff --stat
git diff
```

Confirme que `.env`, `.venv`, `instance`, bancos SQLite e `__pycache__` não aparecem entre os arquivos que serão enviados.

Caso algum `__pycache__` antigo já estivesse versionado:

```powershell
git rm -r --cached app\__pycache__ tests\__pycache__
```

Use esse comando somente para caminhos que realmente existam no índice do Git.

## 8. Criar os commits

Para demonstrar um histórico profissional, organize a atualização em commits coerentes. Como os arquivos serão aplicados de uma vez, uma sequência possível é:

```powershell
git add app migrations run.py wsgi.py requirements.txt requirements-dev.txt pyproject.toml
git commit -m "feat: implement complete task CRUD API"

git add tests
git commit -m "test: add task API integration test suite"

git add .github .vscode Dockerfile docker-compose.yml .dockerignore .editorconfig .gitattributes .gitignore .env.example
git commit -m "chore: add CI Docker and development configuration"

git add README.md docs LICENSE
git commit -m "docs: document API setup endpoints and Git workflow"
```

Se preferir um único commit, use:

```powershell
git add .
git commit -m "feat: complete task CRUD API with tests and CI"
```

Não divida commits apenas para aumentar artificialmente a quantidade. Cada commit deve representar uma mudança lógica.

## 9. Enviar ao GitHub

```powershell
git status
git log --oneline -5
git push origin main
```

Depois do push, abra a guia `Actions` no GitHub e confirme que o workflow `CI` ficou verde.

## 10. Descrição recomendada do repositório

Use no campo **About** do GitHub:

```text
Production-style Flask REST API with complete task CRUD, SQLAlchemy, migrations, validation, tests, Docker and CI.
```

Tópicos recomendados:

```text
python
flask
rest-api
sqlalchemy
pytest
sqlite
docker
github-actions
clean-architecture
backend
```

## 11. Fluxo de teste manual no PowerShell

Criar uma tarefa:

```powershell
$body = @{
    title = "Preparar portfólio Backend Python"
    description = "Revisar README, testes e GitHub Actions"
    status = "in_progress"
    priority = "high"
    due_date = "2026-07-15"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:5000/api/v1/tasks" `
    -ContentType "application/json" `
    -Body $body
```

Listar tarefas:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/v1/tasks"
```

Atualizar parcialmente a tarefa 1:

```powershell
$body = @{ status = "completed" } | ConvertTo-Json

Invoke-RestMethod `
    -Method Patch `
    -Uri "http://127.0.0.1:5000/api/v1/tasks/1" `
    -ContentType "application/json" `
    -Body $body
```

Excluir a tarefa 1:

```powershell
Invoke-RestMethod `
    -Method Delete `
    -Uri "http://127.0.0.1:5000/api/v1/tasks/1"
```
