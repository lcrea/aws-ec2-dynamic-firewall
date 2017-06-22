import json
import os


class Configuration:
    aws_keys = {
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
        'profile_name': None,
        'region_name': None,
    }

    def __init__(self, c_path=None, c_obj=None):
        """

        :param c_path:
        :param c_obj:
        """
        if c_obj:
            c_user_settings = c_obj
        else:
            c_user_settings = self.load_config(c_path)

        # Partially optional
        self.ec2_ids = c_user_settings.get('EC2_Instance_Ids', list())
        self.aws_keys = self._get_keys(c_user_settings)

        # Mandatory
        self.group_id = c_user_settings['Security_Group']['Id']
        self.ping = c_user_settings['Security_Group']['Ping']
        self.rules = c_user_settings['Security_Group']['RulesIN']

    @staticmethod
    def load_config(c_path):
        """

        :param c_path:
        :return:
        """
        with open(c_path, mode='r', encoding='utf-8') as cf:
            return json.load(cf)

    def _get_keys(self, user_settings):
        """

        :param user_settings:
        :return:
        """
        env_keys = {
            'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'profile_name': os.environ.get('AWS_PROFILE'),
            'region_name': os.environ.get('AWS_DEFAULT_REGION'),
        }

        if env_keys != self.aws_keys:
            return env_keys
        else:
            return {
                'aws_access_key_id': user_settings.get(
                    'AWS_ACCESS_KEY_ID'
                ),
                'aws_secret_access_key': user_settings.get(
                    'AWS_SECRET_ACCESS_KEY'
                ),
                'profile_name': user_settings.get(
                    'AWS_PROFILE'
                ),
                'region_name': user_settings.get(
                    'AWS_DEFAULT_REGION'
                ),
            }


###############################################################################
# Utilities
def find_config(c_dirs, c_filename='config.json'):
    """

    :param c_dirs:
    :param c_filename:
    :return:
    """
    for cd in c_dirs:
        cp = os.path.join(cd, c_filename)
        if os.path.isfile(cp):
            return cp
