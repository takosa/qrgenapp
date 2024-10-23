FROM python:3.12


WORKDIR /app

EXPOSE 8501


COPY app.py .
COPY requirements.txt .

RUN pip3 install -r requirements.txt
RUN apt update && apt install -y ttf-mscorefonts-installer
RUN fc-cache -f

CMD streamlit run app.py