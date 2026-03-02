# IMAGEM QUE VAI RODAR
FROM python:3.12-slim 

WORKDIR /app

# TIRA O BUFFER DO TERMINAL DO PYTHON
ENV PYTHONUNBUFFERED=1

COPY marketplace/server/requirements.txt .

# INSTALA OS REQUERIMENTOS DO PROJETO
RUN pip install --no-cache-dir -r requirements.txt

# COPIA AS COISAS DO PROTO
COPY generated ./generated

# ATUALIZA A ESTRUTURA PRO PYTHON
COPY marketplace/server ./marketplace/server

# EXPÕE A PORTA
EXPOSE 50051

# RODA O CÓDIGO
CMD ["python", "-m", "marketplace.server.main"]