FROM python:3.12-bookworm

COPY . /app
WORKDIR /app
RUN apt install curl
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup.sh
RUN chmod +x rustup.sh && ./rustup.sh -y
ENV PATH /root/.cargo/bin:$PATH
RUN pip install -r requirements.txt
RUN playwright install --with-deps
RUN pip install fastapi[standard]
CMD ["fastapi", "run"]
