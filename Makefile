.PHONY: help test clean download

S3_PATH = "s3://pennsieve-ops-use1/testing-resources/video-processor/"
export S3_PATH

.DEFAULT: help
help:
	@echo "Make Help"
	@echo "make test     - build and spin up docker containers, run tests"
	@echo "make clean    - remove docker containers"
	@echo "make download - download resources for all tests"

test: download
	docker-compose build
	docker-compose up --exit-code-from=video_processor_test video_processor_test

clean:
	docker-compose down
	docker-compose rm
	find . -name "*pycache*" -o -name "*.pyc" | xargs rm -rf

download:
	aws s3 sync $(S3_PATH) ./
