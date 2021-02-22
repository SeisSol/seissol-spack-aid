#!/usr/bin/env python3

from aux import Aux
import argparse
import os
import jinja2


cmd_parser = argparse.ArgumentParser()
cmd_parser.add_argument('-c','--compiler', help='compiler suite and version')
cmd_parser.add_argument('--mpi', help='specific mpi implementation, options and version')
cmd_parser.add_argument('--gpu', nargs='?', default=None, help='specific gpu API/lib version')
cmd_parser.add_argument('--builder_image', help='custom builder spack image')
cmd_parser.add_argument('--target_image', help='target os and its version')
cmd_parser.add_argument('--arch_family', help='target image arch family e.g., amd64, arm64, ppc64le')
cmd_parser.add_argument('--arch', nargs='?', default=None, help='specific architecture of a family')
cmd_parser.add_argument('-i', '--input_dir', help='input directory')
cmd_parser.add_argument('-o', '--output_dir', help='output directory')
args = cmd_parser.parse_args()


def write_to_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content + '\n')
    

if not os.path.exists(args.input_dir):
    raise RuntimeError('Cannot open directory with templates')

template_loader = jinja2.FileSystemLoader(searchpath=args.input_dir)
template_env = jinja2.Environment(loader=template_loader)

template = template_env.get_template('spack.yaml.t')
os_map = {'ubuntu-1804': 'ubuntu:18.04',
          'ubuntu-1604': 'ubuntu:16.04',
          'centos-7': 'centos:7',
          'centos-6': 'centos:6'}

package_manager = {'ubuntu-1804': 'apt',
                   'ubuntu-1604': 'apt',
                   'centos-7': 'yum',
                   'centos-6': 'yum'}

spack_spec = template.render(compiler=args.compiler, 
                             mpi=args.mpi,
                             gpu=args.gpu,
                             arch_family=Aux.adjust_arch_family(args.arch_family),
                             arch=args.arch,
                             builder_image=args.builder_image,
                             target_image=os_map[args.target_image],
                             install_command=package_manager[args.target_image])
print(spack_spec)

if not os.path.exists(args.output_dir):
    raise RuntimeError('Cannot open the output directory')


Aux.write_to_file(file_path=os.path.join(args.output_dir, 'spack.yaml'), 
                  content=spack_spec)
