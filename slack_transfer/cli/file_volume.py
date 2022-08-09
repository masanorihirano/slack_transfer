import argparse
import math

from slack_transfer._base import CommonNoLocalVolumeClient


def set_parser_file_volume(parser: argparse.ArgumentParser) -> None:
    """See file_volume section in :doc:`../../../user_guide/cli`"""
    parser.add_argument(
        "--token",
        type=str,
        required=True,
        help="Token obtained from slack. Starts with `xoxb-`",
    )
    parser.add_argument(
        "--channel_ids",
        type=str,
        default=None,
        help="channel ids you want to check the total volume of files. If not set, set to all available channels. "
        + "Set by comma-separation for multiple inputs",
    )
    parser.add_argument(
        "--auto_join",
        action="store_true",
        help="if bot is not in channel automatically join when this flag is used.",
    )


def main_file_volume(args: argparse.Namespace) -> None:
    """See file_volume section in :doc:`../../../user_guide/cli`"""
    client = CommonNoLocalVolumeClient(token=args.token)
    volume = client.get_file_volumes(
        channel_ids=(
            args.channel_ids.split(",") if args.channel_ids is not None else None
        )
    )
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]
    i_units = math.floor(math.log(volume, 1024)) if volume > 0 else 0
    size = round(volume / 1024**i_units, 2)

    print(f"{size} {units[i_units]} (Actual download size is usually smaller.)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    set_parser_file_volume(parser=parser)
    args = parser.parse_args()
    main_file_volume(args=args)
