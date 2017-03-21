import os
import warnings
from unittest import TestCase

from distribrewed.core.defaults import load_from_env
from distribrewed.core.utils.coreutils import parse_config
from tests.helpers import get_full_file_path


class TestParseConfig(TestCase):
    def test_empty_config(self):
        warnings.simplefilter("ignore", ResourceWarning)
        config_file = get_full_file_path('utils/test_parse_config_empty.yml')
        config = parse_config(config_file)

        self.assertIsNotNone(config)
        self.assertEqual(config.file, config_file)

        self.assertIsNotNone(config.master)
        self.assertIsInstance(config.workers, list)
        self.assertEqual(len(config.workers), 0)

        self.assertIsNotNone(config.communication)
        self.assertEqual(config.communication.ip, '0.0.0.0')
        self.assertEqual(config.communication.master_port, 9991)
        self.assertEqual(config.communication.worker_port, 9992)

    def test_communication_config(self):
        warnings.simplefilter("ignore", ResourceWarning)
        config_file = get_full_file_path('utils/test_parse_config_full.yml')
        config = parse_config(config_file)

        self.assertIsNotNone(config)
        self.assertEqual(config.file, config_file)

        self.assertIsNotNone(config.communication)
        self.assertEqual(config.communication.ip, '192.168.1.77')
        self.assertEqual(config.communication.master_port, 9995)
        self.assertEqual(config.communication.worker_port, 9996)

        self.assertIsNotNone(config.master)
        self.assertEqual(config.master.name, 'BrewMaster')

        self.assertIsInstance(config.workers, list)
        self.assertEqual(len(config.workers), 3)
        # TODO: BETTER WORKER CONFIG TESTS


class TestParseConfigEnv(TestCase):
    MASTER_IP = '1.1.1.1'
    MASTER_PORT = '1234'
    WORKER_PORT = '4321'

    def setUp(self):
        os.environ['MASTER_IP'] = '1.1.1.1'
        os.environ['MASTER_PORT'] = '1234'
        os.environ['WORKER_PORT'] = '4321'
        load_from_env()

    def tearDown(self):
        del os.environ['MASTER_IP']
        del os.environ['MASTER_PORT']
        del os.environ['WORKER_PORT']
        load_from_env()

    def test_empty_config_env_vars(self):
        warnings.simplefilter("ignore", ResourceWarning)
        config = parse_config(get_full_file_path('utils/test_parse_config_empty.yml'))
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.communication)
        self.assertEqual(config.communication.ip, self.MASTER_IP)
        self.assertEqual(config.communication.master_port, int(self.MASTER_PORT))
        self.assertEqual(config.communication.worker_port, int(self.WORKER_PORT))
