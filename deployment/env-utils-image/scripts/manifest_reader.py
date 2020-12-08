#!/usr/bin/env python3

import json
import argparse
import sys
import os.path


class ExitCode:
    SUCCESS = 0
    FAILURE = 1


def get_image_digest_from_file(file, arch):
    if not (args.file and os.path.isfile(args.file)):
        raise ValueError('file is not provided or contains a typo. Please, refer to the docs')

    with open(args.file) as file:
        table =  json.load(file)
        return get_image_digest_from_manifest(table, arch)


def get_image_digest_from_manifest(table, target):
    try:
        system, arch = target.split('/')
    except ValueError:
        raise ValueError(f'architecture format is <os>/<platform>, given: {target}')

    for item in table['manifests']:
        platform = item['platform']
        if arch == platform['architecture'] and system == platform['os']:
            return item['digest']

    raise ValueError(f'could not find digest in a given manifest file for: {args.arch}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='find default packages for spack')
    parser.add_argument('-f', '--file', type=str, help="shows output")
    parser.add_argument('-a', '--arch', type=str, default='linux/amd64', help="denote as buildable")
    args = parser.parse_args()

    try: 
        digest = get_image_digest_from_file(file=args.file, arch=args.arch)
        print(digest)
        sys.exit(ExitCode.SUCCESS)
    except ValueError as err:
        print(err)
        sys.exit(ExitCode.FAILURE)
