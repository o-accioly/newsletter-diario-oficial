# Usar uma imagem base do Python
FROM python:3.9-slim

# Instalar dependências necessárias para o Selenium
RUN apt-get update && apt-get install -y \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos necessários
COPY requirements.txt requirements.txt
COPY newsletter.py newsletter.py

# Instalar as dependências
RUN pip install -r requirements.txt

# Comando para rodar o script
CMD ["python", "newsletter.py"]