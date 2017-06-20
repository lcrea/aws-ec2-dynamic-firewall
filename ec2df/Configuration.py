import json
import os


class Configuration:
    aws_keys = {
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
        'profile_name': None,
        'region_name': None,
    }

    def __init__(self, file_name='config.json'):
        """

        :param file_name:
        """
        c_dirs = (
            os.getcwd(),
            os.path.join(os.environ['HOME'], '.ec2df'),
            '/etc'
        )

        for c_dir in c_dirs:
            c_path = os.path.join(c_dir, file_name)
            if os.path.isfile(c_path):
                with open(c_path, mode='r', encoding='utf-8') as c_file:
                    c_user_settings = json.load(c_file)
                break
        else:
            raise FileNotFoundError('{0}: missing'.format(file_name))

        # Optional
        self.ec2_ids = c_user_settings.get('EC2_Instance_Ids', list())
        self.aws_keys = self._get_keys(c_user_settings)

        # Mandatory
        self.group_id = c_user_settings['Security_Group']['Id']
        self.ping = c_user_settings['Security_Group']['Ping']
        self.rules = c_user_settings['Security_Group']['RulesIN']

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
