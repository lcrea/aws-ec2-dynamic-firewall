"""SECURITY NOTE [ Level: WARNING ]

Those tests are entirely based on a config.test.json file and, most of them,
require a live communication with AWS servers.

Most of the changes applied to the instances will be revoked when tests are
completed.
Anyway, please consider to use a proper configuration settings!
"""
from ec2df.Configuration import Configuration, find_config
from ec2df.SecurityRules import SecurityRules, get_ip
from ec2df.shell import CONFIG_DIRS

import boto3
import re
import unittest


config_path = find_config(CONFIG_DIRS, c_filename='config.test.json')
config_obj = Configuration(c_path=config_path)

aws_session = boto3.Session(**config_obj.aws_keys)
ec2_resource = aws_session.resource('ec2')


class TestSecurityRules(unittest.TestCase):
    def setUp(self):
        self.rules = SecurityRules(ec2_resource, config_obj)

    def test_securityrules_init(self):
        """If configuration values are right a SecurityRules should be returned
        """
        self.assertIsInstance(self.rules, SecurityRules)

    def test_getip_format(self):
        """Test if the IP address is a str in CIDR notation
        """
        ip = get_ip()
        self.assertIsInstance(ip, str, msg="IP is not a str: {}".format(ip))

        # Check for this structure: 0.0.0.0/0 - 000.000.000.000/00
        res = re.search(r"""^
                            ([0-9]{1,3})\.  # first octet
                            ([0-9]{1,3})\.  # second octet
                            ([0-9]{1,3})\.  # third octet
                            ([0-9]{1,3})    # fourth octet
                            /([0-9]{1,2})   # CIDR notation
                            $""", ip, re.VERBOSE)
        self.assertIsNotNone(res, msg="Wrong IP format: {}".format(ip))

    def test_generate_response(self):
        res = self.rules.generate()
        self.assertIsInstance(res, list, msg="Wrong type returned")
        self.assertGreater(len(res), 0, msg="Response is empty")
        self.assertIsInstance(res[0], dict, msg="Wrong response structure")

    def test_generate_with_without_ping(self):
        # force removing any config rules
        self.rules.config_set = list()

        for case in [True, False]:
            # reset the test
            self.rules.request_set = list()

            with self.subTest(case=case):
                self.rules.ping = case
                res = self.rules.generate()
                if case:
                    self.assertIsInstance(res[0], dict, msg="Wrong type")
                    self.assertEqual(len(res), 2, msg="Wrong structure")
                else:
                    self.assertIsInstance(res, list, msg="Wrong type")
                    self.assertEqual(len(res), 0, msg="Response not empty")

    def test_generate_happens_only_once(self):
        """If a request has already been generated, it simply returns it
        """
        # case 1: force new values, changing directly the attribute
        tmpl = {'test_key': 'test_value'}
        self.rules.request_set = tmpl
        rules1 = self.rules.generate()

        # case 2: force generate a new rule set from the configuration
        self.rules.request_set = list()
        rules2 = self.rules.generate()

        self.assertIsNot(rules1, rules2, msg="Rules values should differ")
        self.assertIs(rules1, tmpl, msg="Wrong value returned")
        self.assertIsInstance(rules2[0], dict, msg="The list is empty")

    def test_test_request_set_priority(self):
        """Check if test_request_set has higher priority on config set
        """
        # cleanup every existing rules on AWS
        self.rules.clear_all()

        # upload the test version
        tmpl = [{
            'IpProtocol': 'udp',
            'FromPort': 2222,
            'ToPort': 3333,
            'UserIdGroupPairs': [],
            'IpRanges': [{'CidrIp': '192.168.1.111/32'}],
            'Ipv6Ranges': [],
            'PrefixListIds': []
        }]
        self.rules._test_request_set = tmpl
        self.rules.generate()
        self.rules.apply()
        res = self.rules.get_all()

        # AWS should return the test version and not the one generated
        self.assertEqual(res, tmpl)

    def test_clearall_response(self):
        """Test clear_all response in whatever condition the security group is
        """
        self.rules.generate()
        self.rules.apply()

        # case 1 - this contains HTTP Response
        res1 = self.rules.clear_all()
        # case 2 - this must be empty: the double call ensures that
        res2 = self.rules.clear_all()

        self.assertNotEqual(res1, res2, msg="Empty/Full replies must differ")
        # res1 HTTP response should contain the status code
        self.assertEqual(res1['ResponseMetadata']['HTTPStatusCode'], 200,
                         msg="Wrong response from AWS servers")
        # res2 should be empty
        self.assertEqual(res2, {}, msg="Response is not empty")

    def test_getall_response(self):
        """Test get_all response in whatever condition the security group is
        """
        # case 1 - this contains the rules set
        self.rules.generate()
        self.rules.apply()
        res1 = self.rules.get_all()

        # case 2 - this should be empty
        self.rules._test_request_set = res1
        self.rules.clear_all()
        res2 = self.rules.get_all()

        self.assertNotEqual(res1, res2, msg="Empty/Full replies must differ")
        # res1 response should include a dict of rules set
        self.assertIsInstance(res1[0], dict,
                              msg="Wrong response form AWS servers")
        # res 2 should be empty
        self.assertEqual(res2, [], msg="Response is not empty")


if __name__ == '__main__':
    unittest.main()
