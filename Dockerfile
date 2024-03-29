ARG version=0.32.0

FROM --platform=${BUILDPLATFORM} python:3.11.1-alpine3.17
ARG version
ARG TARGETPLATFORM

WORKDIR /app
ADD /client /app/client
ADD /models /app/models
ADD /scraper /app/scraper
ADD config.py /app/config.py
ADD main.py /app/main.py
ADD log.py /app/log.py
ADD requirements.txt /app/requirements.txt
RUN apk add ttf-dejavu ttf-liberation ttf-freefont ttf-opensans ttf-font-awesome
RUN pip install -r requirements.txt
RUN echo "http://dl-cdn.alpinelinux.org/alpine/v3.16/community" >> /etc/apk/repositories
RUN apk add firefox-esr ca-certificates curl --no-cache  \
    && if [ ${TARGETPLATFORM} = "linux/amd64" ]; then \
        DOWNLOAD_ARCH="linux64" ; \
      else \
        DOWNLOAD_ARCH="linux-aarch64" ; \
      fi \
    && curl -L https://github.com/mozilla/geckodriver/releases/download/v${version}/geckodriver-v${version}-${DOWNLOAD_ARCH}.tar.gz | tar xz -C /usr/local/bin \
    && chmod +x /usr/local/bin/geckodriver \
    && apk del curl
RUN printf 'FIREFOX_PATH="/usr/bin/firefox-esr" \n\
HEADLESS=True \n\
TIMEOUT=25 \n\
API="https://api.scamscan.net" \n\
IP=""' >> .env

CMD ["python", "main.py"]
