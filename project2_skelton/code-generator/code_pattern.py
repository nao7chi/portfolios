#出力ファイルのテンプレート部分

run_py_head = """#!/usr/bin/env cs_python

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
"""

run_py_mid1 = """
memcpy_dtype = MemcpyDataType.MEMCPY_32BIT
memcpy_order = MemcpyOrder.ROW_MAJOR

runner = SdkRuntime(args.name, cmaddr=args.cmaddr)
"""
run_py_mid2 = """
runner.load()
runner.run()
"""

run_py_launch = """
runner.launch(\"main\", nonblock=True)
"""

run_py_tail = """
runner.stop()

mask = result != 0.0

result = result[mask]

if result.size == 0:
    result = np.append(result,0.0)

print(result)"""

layout_head = """param WIDTH: i16 ;         
param HEIGHT: i16 ;              

const c2d = @import_module("<collectives_2d/params>");

const memcpy = @import_module( "<memcpy/get_params>", .{
    .width = WIDTH,
    .height = HEIGHT,
});

layout {

  @set_rectangle(WIDTH,HEIGHT);

  var py:i16 = 0;
  while(py < HEIGHT) : (py += 1){
    var px:i16 = 0;
    while(px < WIDTH) : (px += 1){
        const memcpy_params = memcpy.get_params(px);

        const c2d_params = c2d.get_params(px,py,.{
          .x_colors = .{
           @get_color(0),
           @get_color(1)
         },
         .x_entrypoints = .{
           @get_local_task_id(2),
           @get_local_task_id(3)
         },
         .y_colors = .{
           @get_color(4),
           @get_color(5)
         },
         .y_entrypoints = .{
           @get_local_task_id(6),
           @get_local_task_id(7)
         },
        });

        var params: comptime_struct = .{
            .memcpy_params = memcpy_params,
            .c2d_params = c2d_params,
        };

        @set_tile_code(px,py,"pe_program.csl",params);
    }
  }
"""

layout_tail = """  @export_name("result", [*]f32, true);
  @export_name("main", fn()void);
}"""

pe_program_head = """param memcpy_params: comptime_struct;
param c2d_params: comptime_struct;

const sys_mod = @import_module("<memcpy/memcpy>", memcpy_params);
const mpi_x = @import_module("<collectives_2d/pe>", .{ .dim_params = c2d_params.x });
const mpi_y = @import_module("<collectives_2d/pe>", .{ .dim_params = c2d_params.y });

const w = @get_rectangle().width;  
const h = @get_rectangle().height; 

var send = @zeros([1]f32);
var recv = @zeros([1]f32);
var recv_x = @zeros([w]f32);
var recv_y = @zeros([h]f32);

var re_result: f32;
var re_count: u16;
var px: u16;
var py: u16;
"""

pe_program_main = """
fn main() void{

    mpi_x.init();
    mpi_y.init();

    px = mpi_x.pe_id;
    py = mpi_y.pe_id;
    re_result = 0.0;
    re_count = 1;
"""

pe_program_reduce_head = """
task reduce() void {
    var tmp:f32 = 0.0;"""

pe_program_reduce_mid = """
    send[0] = tmp;
    var send_buf = @ptrcast([*]u32, &send);
    var recv_buf = @ptrcast([*]u32, &recv_x);

    mpi_x.gather(0, send_buf, recv_buf, 1, reduce_y_id);
}

task reduce_y() void {

    if (px == 0){
        var tmp :f32 = 0.0;
        for (recv_x) |i|{
            tmp += i;
        }
        send[0] = tmp;
    }

    var send_buf = @ptrcast([*]u32, &send);
    var recv_buf = @ptrcast([*]u32, &recv_y);

    mpi_y.gather(0, send_buf, recv_buf, 1, bcas_x_id);
}

task bcas_x() void{

    var tmp : f32 = 0.0;

    if(px == 0){
        if(py == 0){

            for(recv_y) |i|{
                tmp += i;
            }

            send[0] = tmp;
        }
    }

    send[0] = tmp;
    var send_buf = @ptrcast([*]u32, &send);
    var recv_buf = @ptrcast([*]u32, &recv);

    if (0 == px) {
        mpi_x.broadcast(0, send_buf, 1, bcas_y_id);
    } else {
        mpi_x.broadcast(0, recv_buf, 1, bcas_y_id);
    }
}

task bcas_y() void{

    if(px != 0){
        send[0] = recv[0];
    }

    var send_buf = @ptrcast([*]u32, &send);
    var recv_buf = @ptrcast([*]u32, &recv);

    if (0 == py) {
        mpi_y.broadcast(0, send_buf, 1,assign_id);
    } else {
        mpi_y.broadcast(0, recv_buf, 1,assign_id);
    }
}

task assign() void{

    re_result = recv[0];

    if(px == 0){
        if(py == 0){
            re_result = send[0];
        }
    }"""

commands_head = """#!/usr/bin/env bash

set -e
"""