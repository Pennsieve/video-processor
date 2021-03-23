# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-test:43b7408 as test

RUN apk add --no-cache ffmpeg

WORKDIR /app

COPY requirements.txt ./

RUN  pip install --no-cache-dir -r requirements.txt

COPY video_processor ./video_processor

COPY tests ./tests

COPY run.py ./run.py

ENTRYPOINT [""]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor:43b7408 as prod

RUN apk add --no-cache ffmpeg

WORKDIR /app

COPY requirements.txt ./

RUN  pip install --no-cache-dir -r requirements.txt

COPY video_processor ./video_processor

COPY run.py ./run.py

ENTRYPOINT [""]
