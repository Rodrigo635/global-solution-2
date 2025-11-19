# Global Solution 2

Projeto desenvolvido para a Global Solution 2 da **FIAP**.

## Documentação do projeto
* **Global Solution 2**: [Documentação da solução](https://docs.google.com/document/d/1zEIgvzu84Ja9GmOHL1CJsRCb0wIlL_8X3E53fJUdhJs/edit?usp=sharing)

## 📺 Vídeo apresentando o projeto
* **Global Solution 2**: [Apresentação da solução](https://www.youtube.com/watch?v=-cecIOttRJU)

---

## 🚀 Como rodar o projeto local
#### Pré‑requisitos

* Python 3.14 ou +
* Pip atualizado

Pós fazer o download dos arquivos desse repositório, dentro da pasta rode os comandos abaixo:
#### Passos para iniciar

Para Windows
```bash
py -m venv env                         # cria a env
env\scripts\activate                   # ativa a env
pip install -r requirements.txt        # inicia o servidor de desenvolvimento
py manage.py makemigrations            # verifica as migrações
py manage.py migrate                   # realiza as migrações
py manage.py runserver                 # roda o projeto local
```

Para Linux
```bash
python3.14 -m venv env                 # cria a env
source env/bin/activate                # ativa a env
pip install -r requirements.txt        # inicia o servidor de desenvolvimento
python3.14 manage.py makemigrations    # verifica as migrações
python3.14 manage.py migrate           # realiza as migrações
python3.14 manage.py runserver         # roda o projeto local
```

Após a rodar o comando 'runserver', a aplicação estará disponível em:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

