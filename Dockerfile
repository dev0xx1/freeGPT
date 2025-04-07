FROM python:3.12

WORKDIR /app

COPY requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "scripts/run_agent.py"]
