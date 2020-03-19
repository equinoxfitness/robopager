import sys
from datacoco_core.config import config
from datacoco_secretsmanager import SecretsManager


class ConfigWrapper:
    """
    Wrapper file for config management for robopager
    """

    @staticmethod
    def extend_parser(parser):
        parser.add_argument(
            "-cf",
            "--config",
            required=True,
            default="core",
            help="""
                choose whether to use secret_manager or
                datacoco_core to retrieve credentials
                """,
            choices=["secret_manager", "core"],
        )

        if "core" in sys.argv:
            parser.add_argument(
                "-p",
                "--path",
                default="etl.cfg",
                help="""
            enter the path direct to the config file
            """,
            )

        return parser

    @staticmethod
    def process_config(args):
        if args.config == "secret_manager":
            conf = SecretsManager().get_config(
                project_name="maximilian", team_name="data"
            )
        elif args.config == "core":
            conf = config(args.path)

        return conf
