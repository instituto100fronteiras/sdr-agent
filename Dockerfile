FROM python:3.12-slim

# Evita arquivos .pyc e buffer de saída
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para compilação (se houver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do projeto
COPY . .

# Garante permissão de execução no script de entrada
RUN chmod +x entrypoint.sh

# Expõe a porta do webhook (padrão 5000)
EXPOSE 5000

# Comando de inicialização
CMD ["./entrypoint.sh"]
