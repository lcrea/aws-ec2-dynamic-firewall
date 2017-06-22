import boto3
import click
import os

from .Configuration import Configuration, find_config
from .EC2Instances import EC2Instances
from .SecurityRules import get_ip
from .SecurityRules import SecurityRules


CONFIG_DIRS = (
    os.getcwd(),
    os.path.join(os.environ['HOME'], '.ec2df'),
    '/etc'
)
NAME = os.path.basename(os.path.dirname(__file__))
VERSION = '0.1.0alpha2'


###############################################################################
# Command line interface

# @click.option('--config-file', default=True, help="")
# @click.option('--ip', default=True, help="")
# @click.option('--group-id', default=True, help="")
# @click.option('--ec2-id', default=True, help="")
@click.group()
@click.version_option(VERSION, message=VERSION)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand != 'myip':
        try:
            c_file = find_config(CONFIG_DIRS)
            user_config = Configuration(c_file)
        except FileNotFoundError as e:
            click.echo('ERROR -> {}'.format(e), err=True)
            exit(1)

        session = boto3.Session(**user_config.aws_keys)
        ctx.obj['resource'] = session.resource('ec2')
        ctx.obj['config'] = user_config


@cli.command('myip', short_help="")
def myip():
    ip = get_ip()
    click.echo(ip)


@cli.command('open', short_help="")
@click.pass_context
def open_ports(ctx):
    user_config = ctx.obj['config']
    res = ctx.obj['resource']

    rules = SecurityRules(res, user_config)
    ec2 = EC2Instances(res)

    click.echo('Clearing previous rules')
    rules.clear_all()

    click.echo('Generating new ones and loading them')
    rules.generate()
    rules.apply()

    click.echo('Applying security group to EC2 instances')
    ec2.select_instances(user_config.ec2_ids)
    ec2.apply_rules(user_config.group_id)

    click.echo('Process completed: OK')


@cli.command('close', short_help="")
@click.pass_context
def close_ports(ctx):
    user_config = ctx.obj['config']
    ec2 = EC2Instances(ctx.obj['resource'])

    click.echo('Revoking security group from EC2 instances')
    ec2.select_instances(user_config.ec2_ids)
    ec2.revoke_rules(user_config.group_id)

    click.echo('Process completed: OK')
