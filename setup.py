#!/usr/bin/env python
import argparse
import sys
import latch
import os
import shutil
from latch.parsing import parser as swagger_parser
from latch.codegen import generators
parser = argparse.ArgumentParser(description='Setup for latch projects')
subparsers = parser.add_subparsers()

new_project = subparsers.add_parser('newproject', help="Start a new project from a swagger spec")
new_project.add_argument('swagger', help="Filename of swagger specification")
new_project.add_argument('path', help="Path to where the app should go")

args = parser.parse_args()
parsed_file = swagger_parser.load_from_file(args.swagger)
app_name = parsed_file.info.get('title')
app_root = os.path.join(args.path, app_name)

try:
  try:
    os.mkdir(app_root)
  except FileExistsError as e:
    print("Cannot create new app there, directory already exists!")
    sys.exit()

  api_root = os.path.join(app_root, 'api', parsed_file.basePath.strip('/'))
  os.makedirs(api_root)
  proto_dir = os.path.join(api_root, 'proto')
  py_dir = app_root
  os.makedirs(proto_dir)
  #os.makedirs(py_dir)

  try:
    with open(os.path.join(proto_dir, 'api.proto'), 'wb') as protofile:
      proto_content = generators.swagger_to_protobuf(args.swagger)
      protofile.write(bytearray(proto_content, 'utf-8'))
      protofile.close()

    with open(os.path.join(py_dir, 'app.py'), 'wb') as pyfile:
      py_content = generators.asyncio_gateway(args.swagger)
      pyfile.write(bytearray(py_content, 'utf-8'))
      pyfile.close()

  except:
    raise RuntimeError("Subdirectory creation failure")

except RuntimeError as e:
  shutil.rmtree(app_root)
