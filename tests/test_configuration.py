"""SECURITY NOTE [ Level: SAFE ]

Those tests are entirely based on the config.example.json file and,
furthermore, they are all local: no data is transmitted on AWS servers.
"""
from ec2df.Configuration import Configuration, find_config
from tests.utilities import get_example_config_path

import os
import tempfile
import unittest


ex_config_path = get_example_config_path()
ex_config_obj = Configuration.load_config(ex_config_path)


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.tmp_cfg_obj = ex_config_obj.copy()

    def test_example_config_file(self):
        """Check correctness of the config.example.json file
        """
        config = Configuration(c_path=ex_config_path)
        self.assertIsInstance(config, Configuration)

    def test_path_of_config_file(self):
        with self.assertRaises(FileNotFoundError):
            Configuration(c_path='', c_obj=None)

    def test_config_as_obj_or_file(self):
        """Loading config.json from a file or from an obj must be the same
        """
        cfg_from_file = Configuration(c_path=ex_config_path)
        cfg_from_obj = Configuration(c_obj=self.tmp_cfg_obj)
        self.assertEqual(cfg_from_file.__dict__, cfg_from_obj.__dict__)

    def test_ec2ids_optional(self):
        del(self.tmp_cfg_obj['EC2_Instance_Ids'])
        config = Configuration(c_obj=self.tmp_cfg_obj)
        self.assertIsInstance(config, Configuration)

    def test_securitygroup_is_mandatory(self):
        del (self.tmp_cfg_obj['Security_Group'])
        with self.assertRaises(KeyError):
            Configuration(c_obj=self.tmp_cfg_obj)

    def test_securitygroup_id_is_mandatory(self):
        del (self.tmp_cfg_obj['Security_Group']['Id'])
        with self.assertRaises(KeyError):
            Configuration(c_obj=self.tmp_cfg_obj)

    def test_securitygroup_ping_is_mandatory(self):
        del (self.tmp_cfg_obj['Security_Group']['Ping'])
        with self.assertRaises(KeyError):
            Configuration(c_obj=self.tmp_cfg_obj)

    def test_securitygroup_rulesin_is_mandatory(self):
        del (self.tmp_cfg_obj['Security_Group']['RulesIN'])
        with self.assertRaises(KeyError):
            Configuration(c_obj=self.tmp_cfg_obj)

    def test_awskeys_env_over_config(self):
        """Env keys should have higher priority over config.json settings
        """
        self.tmp_cfg_obj['AWS_ACCESS_KEY_ID'] = 'config_key'
        self.tmp_cfg_obj['AWS_SECRET_ACCESS_KEY'] = 'config_secret_key'
        self.tmp_cfg_obj['AWS_DEFAULT_REGION'] = 'config_region'
        self.tmp_cfg_obj['AWS_PROFILE'] = 'config_profile'

        os.environ['AWS_ACCESS_KEY_ID'] = 'env_key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'env_secret_key'
        os.environ['AWS_DEFAULT_REGION'] = 'env_region'
        os.environ['AWS_PROFILE'] = 'env_profile'

        config = Configuration(c_obj=self.tmp_cfg_obj)
        self.assertEqual(config.aws_keys['profile_name'],
                         os.environ['AWS_PROFILE'])
        self.assertEqual(config.aws_keys['region_name'],
                         os.environ['AWS_DEFAULT_REGION'])
        self.assertEqual(config.aws_keys['aws_access_key_id'],
                         os.environ['AWS_ACCESS_KEY_ID'])
        self.assertEqual(config.aws_keys['aws_secret_access_key'],
                         os.environ['AWS_SECRET_ACCESS_KEY'])

    def test_findconfig_utility(self):
        t_file = tempfile.NamedTemporaryFile()
        t_dirs = [os.path.dirname(t_file.name)]
        t_name = os.path.basename(t_file.name)

        # if file exists
        self.assertEqual(find_config(c_dirs=t_dirs, c_filename=t_name),
                         t_file.name)
        # if file doesn't exist
        self.assertIsNone(find_config(c_dirs=t_dirs, c_filename=''))


if __name__ == '__main__':
    unittest.main()
