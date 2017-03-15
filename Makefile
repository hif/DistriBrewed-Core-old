RUN_DIR ?= ${PWD}
DOCKER_IMAGE_TAG := distribrewed/core

docker-build:
	docker build -t ${DOCKER_IMAGE_TAG} -f ./docker/Dockerfile .

docker-test:
	docker run -it -v ${RUN_DIR}:/app -w /app ${DOCKER_IMAGE_TAG} python -m unittest