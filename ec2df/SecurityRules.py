from urllib.request import urlopen


def get_ip():
    """Dynamically fetch current IP from the Amazon checker

    :return: external IP in CIDR notation (X.X.X.X/32)
    :rtype: str
    """
    with urlopen('http://checkip.amazonaws.com/') as req:
        res = req.read().decode('utf-8').rstrip()
    return '{}/32'.format(res)


class SecurityRules:
    def __init__(self, ec2_res, config):
        """Basic methods to interact with AWS rules through API

        SecurityRules allows to manipulate the rules contents of a single
        security group, based on the configuration provided by the user.

        :param ec2_res: A EC2 boto3.Session resource
        :type ec2_res: object

        :param config: A Configuration instance
        :type config: object
        """
        # EC2 boto3.Session
        self.resource = ec2_res.SecurityGroup(config.group_id)

        # External IP in CIDR notation
        self.ext_ip = ''

        # ID of the security group
        self.group_id = config.group_id

        # Activate ping on firewall? (True/False)
        self.ping = config.ping

        # Rule set provided by user through config file
        self.config_set = config.rules

        # Final generated rule set, ready to be uploaded
        self.request_set = list()

    def generate(self):
        """Generates the rules based on the user configuration

        :return: A list of dictionaries
        :rtype: list
        """
        if not self.request_set:
            if not self.ext_ip:
                self.ext_ip = get_ip()

            if self.ping:
                for port in [8, -1]:
                    tmpl = {
                        "IpProtocol": "icmp",
                        "FromPort": port,
                        "ToPort": -1,
                        "UserIdGroupPairs": [],
                        "IpRanges": [{"CidrIp": self.ext_ip}],
                        "Ipv6Ranges": [],
                        "PrefixListIds": []
                    }
                    self.request_set.append(tmpl)

            for rule in self.config_set:
                tmpl = {
                    "IpProtocol": rule['Protocol'],
                    "FromPort": rule['FromPort'],
                    "ToPort": rule['ToPort'],
                    "UserIdGroupPairs": [],
                    "IpRanges": [{"CidrIp": self.ext_ip}],
                    "Ipv6Ranges": [],
                    "PrefixListIds": []
                }
                self.request_set.append(tmpl)
        return self.request_set

    def get_all(self):
        """Retrieves all the rule set from a specific security group

        :return:
        :rtype: dict
        """
        return self.resource.ip_permissions

    def clear_all(self):
        """

        :return:
        """
        full_set = self.get_all()
        if full_set:
            return self.resource.revoke_ingress(IpPermissions=full_set)

    def apply(self):
        """

        :return:
        """
        self.generate()
        return self.resource.authorize_ingress(IpPermissions=self.request_set)
