"""SECURITY NOTE [ Level: WARNING ]

Those tests are entirely based on a config.test.json file and, most of them,
require a live communication with AWS servers.

Most of the changes applied to the instances will be revoked when tests are
completed.
Anyway, please consider to use a proper configuration settings!
"""
from ec2df.Configuration import Configuration, find_config
from ec2df.EC2Instances import EC2Instances
from ec2df.shell import CONFIG_DIRS

import boto3
import unittest


config_path = find_config(CONFIG_DIRS, c_filename='config.test.json')
config_obj = Configuration(c_path=config_path)

aws_session = boto3.Session(**config_obj.aws_keys)
ec2_resource = aws_session.resource('ec2')


class TestEC2Instances(unittest.TestCase):
    def setUp(self):
        self.ec2 = EC2Instances(ec2_resource)

    def test_ec2instance_init(self):
        """If configuration values are right a EC2Instances should be returned
        """
        self.assertIsInstance(self.ec2, EC2Instances)

    def test_select_instance_ids_priority(self):
        """Specifying instance_ids should have higher priority than None
        """
        input_ids = ['id1', 'id2']
        output_ids = self.ec2.select_instances(input_ids)
        output_all = self.ec2.select_instances()
        self.assertEqual(input_ids, output_ids)
        self.assertNotEqual(input_ids, output_all,
                            msg='At last one EC2 instance should be running!')

    def test_get_security_groups_result_from_all_ec2(self):
        """Retrieves security groups from all the instances (limit: 10)
        """
        self.ec2.select_instances()

        # Limit the test at 10 instances
        for instance in self.ec2.instance_ids[:10]:
            res = self.ec2.resource.Instance(instance)
            sg = self.ec2.get_security_groups(res)
            self.assertIsInstance(sg, set,
                                  msg="Returned value should be a set")
            self.assertGreaterEqual(len(sg), 1,
                                    msg="Security groups should always be "
                                        "greater than 1")

    def test_apply_revoke_sequence(self):
        self.ec2.select_instances(config_obj.ec2_ids)
        res_apply = self.ec2.apply_rules(config_obj.group_id)
        res_revoke = self.ec2.revoke_rules(config_obj.group_id)

        # Check if apply / revoke operations are the same
        self.assertEqual(len(res_apply), len(res_revoke),
                         msg="The number of apply/revoke responses differs")

        # Check if HTTP status code is 200 for both
        for res in zip(res_apply, res_revoke):
            self.assertEqual(res[0][1], res[1][1],
                             msg="HTTP Status code != 200")

    def test_revoke_rules_twice(self):
        """If the method is called more than once no error should be raised
        """
        self.ec2.select_instances(config_obj.ec2_ids)
        res1 = self.ec2.revoke_rules(config_obj.group_id)
        res2 = self.ec2.revoke_rules(config_obj.group_id)

        for res in zip(res1, res2):
            self.assertEqual(res[0][1], res[1][1],
                             msg="HTTP Status code != 200")


if __name__ == '__main__':
    unittest.main()
