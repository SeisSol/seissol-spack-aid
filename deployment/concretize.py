# Example:
#   python3 ./concretize.py -i ./templates -o ./build -c gcc@8.4.0 --mpi openmpi@3.1.5^cuda --os ubuntu:18.04

#spack containerize | sed 's/\(FROM \)\(.*\)\( as builder\)/\1custom-builder\3/'
#spack containerize | sed 's/\(FROM \)\([[:alpha:]]\+:[[:digit:]]\+\.[[:digit:]]\+\)/\1custom-builder/'

import argparse
import os, errno
import jinja2

cmd_parser = argparse.ArgumentParser()
cmd_parser.add_argument('-c','--compiler', help='compiler suite and version')
cmd_parser.add_argument('--mpi', help='specific mpi implementation, options and version')
cmd_parser.add_argument('--os', help='target os and its version')
cmd_parser.add_argument('-i', '--input_dir', help='output directory')
cmd_parser.add_argument('-a', '--arch', help='target image host arch')
cmd_parser.add_argument('-o', '--output_dir', help='directory which contains jinja templates')
args = cmd_parser.parse_args()

OS_TRANSLATION_TABLE = {'ubuntu:16.04' : 'spack/ubuntu-xenial',
                        'ubuntu:18.04' : 'spack/ubuntu-bionic'}

def convert_to_spack_os(os_name):   
    if not OS_TRANSLATION_TABLE[os_name]:
        raise ValueError(f'Currently, your requested os - i.e., {os_name} - is not supported')
    
    return OS_TRANSLATION_TABLE[os_name]


def write_to_file(file_path, content):
    file = open(file_path, 'w')
    file.write(content + '\n')
    file.close()
    

if not os.path.exists(args.input_dir):
    raise RuntimeError('Cannot open directory with templates')

template_loader = jinja2.FileSystemLoader(searchpath=args.input_dir)
template_env = jinja2.Environment(loader=template_loader)

# concretize custom builder image
print('=' * 80)
template = template_env.get_template('Dockerfile.spack.t')
custom_builder = template.render(spack_os = convert_to_spack_os(args.os), compiler=args.compiler)
print(custom_builder)

# concretize spack template
print('=' * 80)
extra_packages = ""
if "cuda" in args.mpi:
    extra_packages = ", cuda"

template = template_env.get_template('spack.yaml.t')
spack_spec = template.render(compiler=args.compiler, mpi=args.mpi, arch=args.arch, os=args.os, extra=extra_packages)
print(spack_spec)


if not os.path.exists(args.output_dir):
    raise RuntimeError('Cannot open the output directory')


write_to_file(file_path=os.path.join(args.output_dir, 'Dockerfile.spack'), 
              content=custom_builder)

write_to_file(file_path=os.path.join(args.output_dir, 'spack.yaml'), 
              content=spack_spec)