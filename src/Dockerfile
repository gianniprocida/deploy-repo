
FROM       python:3.9

WORKDIR    /app

COPY       requirements.txt /app/

RUN        pip install -r requirements.txt

RUN        apt-get update && apt-get install -y vim

COPY       *.py /app/

RUN        chmod a+x *.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8088"]


