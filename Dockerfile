# Usar uma imagem oficial do Python como base
FROM python:3.9-slim

# Atualizar pacotes e instalar dependências para o zbar
RUN apt-get update && apt-get install -y \
    zbar-tools \
    libzbar0 \
    libzbar-dev \
    && apt-get clean

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar os arquivos do projeto para o contêiner
COPY . /app

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta onde o Flask será executado
EXPOSE 5000


# Comando para executar o aplicativo
CMD ["python", "app.py"]
