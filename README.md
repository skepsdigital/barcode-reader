# intro

Use um ambiente virtual para instalar as dependencias do seu projeto:
Criar:
`python -m venv .venv`

Ativar existente:
`source ./.venv/bin/activate`

Para sair do ambiente virtual:
`deactivate`

## instalando dependencias

Instale as dependencias com o comando abaixo, substituindo pelo nome da lib.
`pip3 install <nome> -r requirements.txt`

depois, congele as dependencias:
`pip3 freeze > requirements.txt`

## buildando

`docker build -t meu_app_flask .`
Sendo `meu_app_flask` o nome da sua imagem após o build.

## execução

`docker run -p 5000:5000 meu_app_flask`
Sendo `meu_app_flask` o nome dado à sua imagem.
A primeira porta 5000 é a porta local.
A segunda porta 5000 é a porta do container. Para alterá-la, você precisa alterar o arquivo Dockerfile.


