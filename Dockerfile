FROM python:3.12

RUN pip3 install pipenv

WORKDIR /app

EXPOSE 8501

COPY Pipfile.lock .
COPY app.py .

RUN pipenv sync

CMD streamlit run app.py