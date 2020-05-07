FROM python:alpine AS build
LABEL git="https://github.com/Aeriqu/CroBot"
ARG KYTEA_VERSION=0.4.7

WORKDIR /app

RUN apk add --no-cache build-base libffi-dev && \
wget http://www.phontron.com/kytea/download/kytea-${KYTEA_VERSION}.tar.gz && \
tar xf kytea-${KYTEA_VERSION}.tar.gz && \
cd kytea-${KYTEA_VERSION} && ./configure && make && \
mkdir /app/kytea && make install prefix=/app/kytea

RUN pip install virtualenv && python -m virtualenv venv
COPY /requirements.txt requirements.txt
RUN ./venv/bin/pip install \
--global-option=build_ext \
--global-option="-L/app/kytea/lib/" \
--global-option="-I/app/kytea/include/" \
-r requirements.txt


FROM python:alpine AS runtime
RUN apk add --no-cache libstdc++
WORKDIR /app
COPY --from=build /app/venv venv
# we copy kytea/{bin,include,lib,share}
COPY --from=build /app/kytea/ /usr/local/
ENV PATH="/app/venv/bin:$PATH"
RUN ln -s /usr/local/share/kytea/model.bin

COPY . .
RUN ./db_init.py
CMD ./run.py
