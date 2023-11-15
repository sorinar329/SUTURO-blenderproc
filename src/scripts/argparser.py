import argparse


def get_argparse():
    parser = argparse.ArgumentParser(description='A test program.')
    parser.add_argument("--config_yaml", help="Config file which should be located at /data/yaml")
    parser.add_argument("--output", help="Output directory of annotations and images")
    args = parser.parse_args()

    return args
