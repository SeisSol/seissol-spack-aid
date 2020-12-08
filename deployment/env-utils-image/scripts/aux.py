from manifest_reader import ExitCode, get_image_digest_from_manifest
import subprocess
import json
from io import StringIO
import re


class Aux:
    @classmethod
    def adjust_arch_family(cls, family):
        arch_family_map = {"amd64": "x86_64",
                           "arm64": "aarch64",
                           "ppc64le": "ppc64le"}
        return arch_family_map[family]

    @classmethod
    def write_to_file(cls, file_path, content):
        with open(file_path, 'w') as file:
            file.write(content + '\n')

    @classmethod
    def print_bar(cls):
        text_bar = '=' * 80
        print(text_bar)


class ImageDigest:
    _base_name_pattern = re.compile('(.*)(:.*)')
    _digest_pattern = re.compile('\[(.*@(.*))*\]')
    def __init__(self, image_name, arch_family):
        self._image_name = image_name
        self._arch_family = arch_family
        self._manifest = None
        self._digest = None
        self._check()

    def get_name_with_digest(self):
        self._manifest = self._get_manifest()
        parsed_manifest = json.load(self._manifest)

        try:
            self._digest = get_image_digest_from_manifest(parsed_manifest,
                                                          f'linux/{self._arch_family}')
        except KeyError as err:
            print(f'Warning: buildx failed to retrive digest from {self._image_name}. '
                  f'Trying to use docker inspect')
            self._digest = self._get_image_digest_from_docker()

        return self._glue_name_and_digest()

    def _check(self):
        allowed = ["amd64", "arm64", "ppc64le"]
        if not self._arch_family in allowed:
            allowed_str = ', '.join(allowed)
            raise ValueError(f'allowed arch. {allowed_str}, given {self._arch_family}')

    def _get_manifest(self):
        process = subprocess.run(f'docker manifest inspect {self._image_name}',
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        if process.returncode == ExitCode.SUCCESS:
            return StringIO(process.stdout.decode().rstrip())
        else:
            raise RuntimeError(f'cannot get manifest for image {self._image_name}.\n'
                               f'Docker error: {process.stderr}')

    def _get_image_digest_from_docker(self):
        command = 'docker inspect --format=\'{{.RepoDigests}}\''
        command = f'{command} {self._image_name}'
        process = subprocess.run(f'{command}',
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        if process.returncode == ExitCode.SUCCESS:
            output = process.stdout.decode().rstrip()
            return self._retrive_digest_from_list(output)
        else:
            raise RuntimeError(f'cannot get manifest for image {self._image_name}.\n'
                               f'Docker error: {process.stderr}')

    def _retrive_digest_from_list(self, string):
        match = ImageDigest._digest_pattern.search(string)
        if not (match and match.group(1) and match.group(2)):
            raise RuntimeError(f'cannot retrive digest from: {string}')
        return match.group(2)

    def _glue_name_and_digest(self):
        match = ImageDigest._base_name_pattern.search(self._image_name)
        if not (match and match.group(1)):
            raise RuntimeError(f'cannot retrive a base image name from {self._image_name}')
        return f'{match.group(1)}@{self._digest}'
