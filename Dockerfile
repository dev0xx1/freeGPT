FROM python:3.12

WORKDIR /app

COPY requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt

RUN pip install farcaster

COPY . .

ENV PYTHONPATH=/app
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8


CMD ["python", "scripts/run_agent.py"]
