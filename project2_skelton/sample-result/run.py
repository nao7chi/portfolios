#!/usr/bin/env cs_python

import argparse
import json
import numpy as np

from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime     # pylint: disable=no-name-in-module
from cerebras.sdk.runtime.sdkruntimepybind import MemcpyDataType # pylint: disable=no-name-in-module
from cerebras.sdk.runtime.sdkruntimepybind import MemcpyOrder    # pylint: disable=no-name-in-module
# from cerebras.sdk.sdk_utils import memcpy_view

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="the test name")
parser.add_argument("--cmaddr", help="IP:port for CS system")
args = parser.parse_args()

with open(f"{args.name}/out.json", encoding='utf-8') as json_file:
  compile_data = json.load(json_file)
compile_params = compile_data["params"]           
width =  int(compile_params["WIDTH"])             
height =  int(compile_params["HEIGHT"])                       

datax = [0.2, 0.5, 1.0]
datay = [0.4, 0.7, 1.0]
datax = np.array(datax,dtype=np.float32)
datay = np.array(datay,dtype=np.float32)

memcpy_dtype = MemcpyDataType.MEMCPY_32BIT
memcpy_order = MemcpyOrder.ROW_MAJOR

runner = SdkRuntime(args.name, cmaddr=args.cmaddr)

datax_symbol = runner.get_id('datax')
datay_symbol = runner.get_id('datay')
result_symbol = runner.get_id('result')

runner.load()
runner.run()

runner.memcpy_h2d(datax_symbol, datax, 0, 0, width, height, 0, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
  
runner.memcpy_h2d(datay_symbol, datay, 0, 0, width, height, 0, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
  

runner.launch("main", nonblock=True)

result = np.zeros([3], dtype=np.float32)

runner.memcpy_d2h(result, result_symbol, 0, 0, width, height, 0, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)

runner.stop()

mask = result != 0.0

result = result[mask]

if result.size == 0:
    result = np.append(result,0.0)

print(result)