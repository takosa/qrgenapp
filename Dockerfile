FROM python:3.12

EXPOSE 8501

RUN apt update && apt install -y fonts-noto-cjk

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY app.py .

COPY .streamlit .streamlit

CMD ["streamlit", "run", "app.py"]