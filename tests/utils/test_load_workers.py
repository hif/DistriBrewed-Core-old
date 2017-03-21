import os
import warnings
from unittest import TestCase

from distribrewed.core.defaults import load_from_env
from distribrewed.core.utils.coreutils import parse_config, load_worker
from tests.helpers import get_full_file_path


class TestLoadWorkers(TestCase):
    def test_load_workers(self):
        warnings.simplefilter("ignore", ResourceWarning)
        config_file = get_full_file_path('utils/test_parse_config_full.yml')
        config = parse_config(config_file)
        workers = []
        for worker_config in config.workers:
            workers.append(load_worker(config.communication, worker_config))
