FROM python:3

WORKDIR /root

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "-m", "src.main" ]