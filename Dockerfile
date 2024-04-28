FROM python:3.12

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

COPY init.sh /usr/src/app
RUN chmod +x /usr/src/app/init.sh

ENTRYPOINT [ "/usr/src/app/init.sh", "phi", "ws", "up" ]