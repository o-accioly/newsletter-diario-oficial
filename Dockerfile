# Usar uma imagem base do Python
FROM python:3.9-slim

ENV TZ=America/Sao_Paulo

RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf

# Instale as dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Adicione o repositório do Chrome e instale o Chrome
RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instale o ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

# Defina variáveis de ambiente para o ChromeDriver
ENV PATH="/usr/local/bin/chromedriver:${PATH}"

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos necessários
COPY requirements.txt requirements.txt
COPY newsletter.py newsletter.py
COPY check_health.py check_health.py

# Instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar o script
CMD ["python", "newsletter.py"]