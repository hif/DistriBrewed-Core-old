RUN_DIR ?= ${PWD}
DOCKER_IMAGE_TAG := distribrewed/core

docker-build:
	docker build -t ${DOCKER_IMAGE_TAG} -f ./docker/Dockerfile .

docker-test:
	docker run -it -v ${RUN_DIR}:/app -w /app ${DOCKER_IMAGE_TAG} python -m unittest

TEST_MASTER := TEST_MASTER
TEST_WORKER := TEST_WORKER

docker-test-communication:
	-@docker rm ${TEST_MASTER}
	@docker run -d --name ${TEST_MASTER} -p 9991:9991 -p 9992:9992 -v ${RUN_DIR}:/app -w /app ${DOCKER_IMAGE_TAG} python -u tests/communication/master.py
	@docker run --rm --name ${TEST_WORKER} --net=host -e MASTER_IP=localhost -v ${RUN_DIR}:/app -w /app ${DOCKER_IMAGE_TAG} python -u tests/communication/worker.py
	@docker logs ${TEST_MASTER}
	@docker stop ${TEST_MASTER}
	@docker rm ${TEST_MASTER}

docker-test-communication-kill:
	-@docker stop ${TEST_MASTER}