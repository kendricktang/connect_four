FROM python:3.7
RUN pip install --upgrade pip
COPY . /app
WORKDIR /app
RUN python setup.py install
CMD ["bash", "run.sh"]
