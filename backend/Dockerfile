FROM python:3.13-slim

WORKDIR /backend

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONPATH="/backend:$PYTHONPATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug", "--reload"]
