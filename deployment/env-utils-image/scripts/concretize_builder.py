#!/usr/bin/env python3

from aux import Aux
import argparse
import os
import jinja2


cmd_parser = argparse.ArgumentParser()
cmd_parser.add_argument('-c','--compiler', help='compiler suite and version')
cmd_parser.add_argument('--spack_base_image', help='spack base image')
cmd_parser.add_argument('-i', '--input_dir', help='input directory')
cmd_parser.add_argument('--arch_family', help='target image arch family e.g., amd64, arm64, ppc64le')
cmd_parser.add_argument('-o', '--output_dir', help='output directory')
args = cmd_parser.parse_args()


if not os.path.exists(args.input_dir):
    raise RuntimeError('Cannot open directory with templates')

template_loader = jinja2.FileSystemLoader(searchpath=args.input_dir)
template_env = jinja2.Environment(loader=template_loader)

# concretize custom builder image
Aux.print_bar()
template = template_env.get_template('Dockerfile.spack.t')
custom_builder = template.render(compiler=args.compiler,
                                 spack_base_image=args.spack_base_image,
                                 arch_family=Aux.adjust_arch_family(args.arch_family))
print(custom_builder)

if not os.path.exists(args.output_dir):
    raise RuntimeError('Cannot open the output directory')


Aux.write_to_file(file_path=os.path.join(args.output_dir, f'custom-spack-{args.arch_family}.dockerfile'), 
                  content=custom_builder)