RUN_DIR ?= ${PWD}
DOCKER_IMAGE_TAG := distribrewed/core

docker-build:
	docker build -t ${DOCKER_IMAGE_TAG} -f ./docker/Dockerfile .