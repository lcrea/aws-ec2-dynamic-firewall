class EC2Instances:
    def __init__(self, ec2_res):
        """

        :param ec2_res:
        """
        self.instance_ids = list()
        self.resource = ec2_res
        # self.resource = session_obj.resource('ec2')
        # self.client = session_obj.client('ec2')

    @staticmethod
    def get_security_groups(instance):
        """

        :param instance:
        :return:
        """
        old_groups = instance.describe_attribute(Attribute='groupSet')
        old_groups_list = old_groups['Groups']

        new_groups = set(g['GroupId'] for g in old_groups_list)
        return new_groups

    def select_instances(self, instance_ids=None):
        """

        :param instance_ids:
        :return:
        """
        if instance_ids:
            self.instance_ids = instance_ids
        else:
            obj = self.resource.instances.all()
            self.instance_ids = [instance.id for instance in obj]

        return self.instance_ids

    def apply_rules(self, group_id):
        """

        :param group_id:
        :return:
        """
        res = list()
        for instance in self.instance_ids:
            ec2 = self.resource.Instance(instance)

            # Add the security group to those already existent in the instance.
            security_groups = self.get_security_groups(ec2)
            security_groups.add(group_id)

            # Apply the changes
            r = ec2.modify_attribute(Groups=list(security_groups))
            res.append(r)

        return res

    def revoke_rules(self, group_id):
        """

        :param group_id:
        :return:
        """
        res = list()
        for instance in self.instance_ids:
            ec2 = self.resource.Instance(instance)

            # Remove the security group from those already existent.
            security_groups = self.get_security_groups(ec2)
            security_groups.remove(group_id)

            r = ec2.modify_attribute(Groups=list(security_groups))
            res.append(r)

        return res
