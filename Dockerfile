FROM python:3.9-slim as django
ENV PYTHONUNBUFFERED=1

WORKDIR /src
COPY requirements.txt ./

ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID dev  &&  \
    useradd -m -u $UID -g $GID dev && \
    apt-get update && apt-get install -y libpq-dev  build-essential && \
    pip install -r requirements.txt && \
    apt-get purge -y build-essential && \
    apt-get clean  && \
    rm -rf /var/lib/apt/lists/*
USER dev
CMD ["bash"]
