FROM python:3.12-slim

RUN apt update && apt install golang-go -y

RUN go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest && \
    echo 'export PATH=$PATH:/root/go/bin' >> /etc/profile

COPY . /scaapp

WORKDIR /scaapp
RUN pip install -r requirements.txt

ENV PATH="/root/go/bin:${PATH}"

ENTRYPOINT [ "python", "parsers.py" ]