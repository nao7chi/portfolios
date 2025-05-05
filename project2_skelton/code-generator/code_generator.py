import ast
import sys
import code_pattern

width = 0
height = 0
length = 0
print_val = ""        #最後に出力する変数名を保持
print_type= ""        #最後に出力する変数の型を保持
data_holder = []      #データの変数名を保持
val_holder = []       #変数名を保持
array_holder = []     #転送しない配列を保持
event_holder = []     #各イベントを保持
length_holder = {}    #データの大きさをハッシュマップで保持
task_schedule = []    #タスクスケジュールを保持
reduce_op_holder = [] #reduceの演算子を保持
reduce_da_holder = [] #reduce対象のデータを保持
af_reduce = []        #タスクのうち、reduceの直後に呼ばれるもの
no_af_reduce = []     #af_reduce以外
fndef_code = []       #関数定義をまとめて保持
run_py_code = []      #run.pyのコード
layout_code = []      #layout.cslのコード
pe_program_code = []  #pe_program.cslのコード
commands_code = []    #commands.shのコード


#二次元データを、1次元に変換する関数
def d2_d1(x,w,h) :
    y = []
    l1 = len(x[0])
    l_w:int = l1 / w
    l2 = len(x)
    l_h:int = l2 / h

    for l in range(int(l_w)) :
        tmp1 = int(l_h*l)
        for k in range(int(l_h)) :
            tmp2 = int(l_w * k)
            for i in range(int(l_h)):
                for j in range(int(l_w)):
                    y.append(x[i+tmp1][j+tmp2])
    return y

#reduceの後のタスクかどうかを判別する関数
def divide_af_reduce (l) :
    no_af_reduce.append(l[0])
    for i in range(1,len(l)):
        if l[i-1] == "reduce":
            af_reduce.append(l[i])
        else :
            no_af_reduce.append(l[i])

#1段階目のコード解析を行うクラス
class midcode_gen(ast.NodeVisitor):

    def  __init__(self):

        self.midcode = []       #生成される中間コードのリスト
        self.eventcode = []     #各イベントの内容
        self.data_dim = 0       #データの次元 (1or2)
        self.data_flag = False  #転送データの確認
        self.length = 0         #転送データの大きさ
        self.data_name = ""     #データの名前
        self.map_iter = 0       #mapのループ回数
        self.map_args = []      #mapの引数
        self.zip_iter = 0       #zipのループ回数
        self.zip_args = []      #zipの引数
        self.eventnum = 1       #イベントのナンバリング変数
        self.max_length = 0     #lengthの最大値
    
    def visit_Module(self, node):  

        self.generic_visit(node)  

    def visit_Assign(self, node):  #代入文に対する処理

        var_name = self.visit(node.targets[0])  
        value = self.visit(node.value)          
        
        #各メタ変数への処理
        if value == "Data" :
            self.data_name = f"{var_name}"
        
        elif var_name == "WIDTH":
            global width 
            width = int(value)

        elif var_name == "HEIGHT":
            global height
            height = int(value)

        elif self.data_flag :
            #転送するデータに対する処理、1次元ならそのまま、2次元は1次元に変換

            #1次元データ
            if self.data_dim == 1: 
                value = ast.literal_eval(ast.unparse(node.value))
                self.midcode.append(f"{self.data_name} = {value}")
                data_holder.append(self.data_name)
                self.length = len(value)
                self.data_flag = False

                if self.length % width*height == 0:
                    length_holder.setdefault(self.data_name,(f"{int(self.length / (width*height))}"))
                    if self.max_length < self.length :
                        self.max_length = self.length
                else :  #データが割り切れなければエラー
                    print("length not match PEs")
                    sys.exit()

            #2次元データ        
            elif self.data_dim == 2: 
                value = ast.literal_eval(ast.unparse(node.value))
                value = d2_d1(value,width,height)
                self.midcode.append(f"{self.data_name} = {value}")
                data_holder.append(self.data_name)
                self.length = len(value)
                self.data_flag = False

                if self.length % width*height == 0:
                    length_holder.setdefault(self.data_name,(f"{int(self.length / (width*height))}"))
                    if self.max_length < self.length :
                        self.max_length = self.length
                else :  #データが割り切れなければエラー
                    print("length not match PEs")
                    sys.exit()

            else : #データの次元数が合わないため、エラーとして終了
                print("data.dim is out of range")
                sys.exit()
        
        #各スケルトン関数を解析
        elif value == "map" :
            self.eventcode.append(f"@map({self.map_args[0]}, {self.map_args[1]}_dsd, {var_name}_dsd);")

            if (not var_name in data_holder) and (not var_name in array_holder) :
                #未宣言の配列への代入であれば、配列の情報(名前、大きさ)を保持
                array_holder.append(var_name)
                if self.map_args[1] in data_holder:
                    self.map_iter = int(self.map_iter / (width * height))
                    length_holder.setdefault(var_name, f"{self.map_iter}")
                else :
                    length_holder.setdefault(var_name, f"{self.map_iter}")
            
            self.zip_args = []
        
        elif value == "zipwith" :
            self.eventcode.append(f"@map({self.zip_args[0]}, {self.zip_args[1]}_dsd, {self.zip_args[2]}_dsd,{var_name}_dsd);")
            
            if (not var_name in data_holder) and (not var_name in array_holder) :
                #未宣言の配列への代入であれば、配列の情報(名前、大きさ)を保持
                array_holder.append(var_name)
                if self.zip_args[1] in data_holder:
                    self.zip_iter = int(self.zip_iter / (width * height))
                    length_holder.setdefault(var_name, f"{self.zip_iter}")
                else :
                    length_holder.setdefault(var_name, f"{self.zip_iter}")
            
            self.zip_args = []
        
        elif value == "reduce" :
            self.eventcode.append(f"{var_name} = re_result;")
            if not var_name in val_holder:
                val_holder.append(var_name)

        #通常の関数を解析
        else :
            self.eventcode.append(f"{var_name} = {value};")
            if (not var_name in val_holder) and (not var_name in data_holder):
                val_holder.append(var_name)

    #二項演算に対する処理 
    def visit_BinOp(self, node):   

        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self.visit(node.op)

        return f"{left} {op} {right}"
    
    #各終端ノードに対する処理
    def visit_Name(self, node): 
        return node.id

    def visit_Constant(self, node): 
        return str(node.value)

    def visit_Add(self, node):  
        return "+"
    
    def visit_Sub(self, node):  
        return "-"
    
    def visit_Mult(self, node):  
        return "*"
    
    def visit_Div(self, node):  
        return "/"
    
    #関数呼び出しに対する処理
    def visit_Call(self, node):  
        func = self.visit(node.func)
        args = [self.visit(arg) or "" for arg in node.args]

        if func == "Data" :
            self.data_dim = int(args[0])
            self.data_flag = True
            return "Data"
        
        if isinstance(node.func ,ast.Attribute) :
            attr_name = node.func.attr
            if attr_name == "map" :
                if len(args) != 3: #引数の数が間違っていればエラーとして終了
                    print("wrong number of arguments for map")
                    sys.exit()
                self.map_args = [args[0], args[1]]
                self.map_iter = int(args[2])
                return "map"
            
            elif attr_name == "map_ow" :
                if len(args) != 3: 
                    print("wrong number of arguments for map_ow")
                    sys.exit()
                self.eventcode.append(f"@map({args[0]}, {args[1]}_dsd, {args[1]}_dsd);")
                return ""
            
            elif attr_name == "zipwith" :
                if len(args) != 4: 
                    print("wrong number of arguments for zipwith")
                    sys.exit()
                self.zip_args = [args[0], args[1], args[2]]
                self.zip_iter = int(args[3])
                return "zipwith"
            
            elif attr_name == "zipwith_ow" :
                if len(args) != 4: 
                    print("wrong number of arguments for zipwith_ow")
                    sys.exit()
                self.eventcode.append(f"@map({args[0]}, {args[1]}_dsd, {args[2]}_dsd, {args[1]}_dsd);")
                return ""

            elif attr_name == "reduce":
                if len(args) != 3: 
                    print("wrong number of arguments for reduce")
                    sys.exit()

                if self.eventcode : #イベントコードが空でないなら、それをイベントとしてまとめる
                    event_holder.append(self.eventcode)
                    task_schedule.append(f"event{self.eventnum}")
                    self.eventnum += 1
                    self.eventcode = []
                
                task_schedule.append("reduce")
                reduce_op_holder.append(args[0])
                reduce_da_holder.append(args[1])
                return "reduce"
            
            elif attr_name == "output":
                if len(args) != 2: 
                    print("wrong number of arguments for output")
                    sys.exit()

                global print_val
                print_val = args[0]
                global print_type
                print_type = args[1]
                


            
        args = ", ".join(args)
        return f"{func}({args})"
    
     #関数定義は、後で変換する
    def visit_FunctionDef(self, node):  
        self.midcode.append(ast.unparse(node))

    def visit_Return(self, node):   
        value = self.visit(node.value)
        self.midcode.append(f"    return {value}")

    #コード生成
    def generate_code(self, code):   
        tree = ast.parse(code)
        self.visit(tree)
        if self.eventcode :
            event_holder.append(self.eventcode)
            task_schedule.append(f"event{self.eventnum}")
        task_schedule.append("exit")
        divide_af_reduce(task_schedule)
        global length
        length = self.max_length
        return "\n".join(self.midcode)

#2段階目のコード解析
class code_gen(ast.NodeVisitor):

    def __init__(self):
        self.fndef = [] 

    def visit_Module(self, node):
        self.generic_visit(node)

    def visit_Assign(self, node):
        var_name = self.visit(node.targets[0])  
        value = self.visit(node.value)

        if var_name in data_holder :
            value = ast.literal_eval(ast.unparse(node.value))
            run_py_code.append(f"{var_name} = {value}")

        else :
            self.fndef.append(f"    {var_name} = {value};") 

    def visit_BinOp(self, node):     
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self.visit(node.op)
        return f"({left} {op} {right})"
    
    def visit_Name(self, node):  
        return node.id

    def visit_Constant(self, node):  
        return str(node.value)

    def visit_Add(self, node):  
        return "+"
    
    def visit_Sub(self, node):  
        return "-"
    
    def visit_Mult(self, node):  
        return "*"
    
    def visit_Div(self, node):  
        return "/"
    
    #関数定義に対する処理
    def visit_FunctionDef(self, node):  
        func_name = node.name
        args = [f"{arg.arg}" for arg in node.args.args]
        for i in range(len(args)) :
            if i == 0 :
                args[i] = f"{args[i]} : f32"
            else :
                args[i] = f"{args[i]} : f32"
        args_str = ", ".join(args)
        self.fndef.append(f"fn {func_name}({args_str}) f32{{")

        for stmt in node.body:
            self.visit(stmt)
        
        self.fndef.append("""}
                            """)
    
    def visit_Return(self, node):   
        value = self.visit(node.value)
        self.fndef.append(f"    return {value};")

    #コード生成
    def generate_code(self, mid_code):   
        tree = ast.parse(mid_code)
        self.visit(tree)
        return "\n".join(self.fndef)
           
midconverter = midcode_gen()
converter = code_gen()

args = sys.argv

#引数のファイルが一つでなければエラー
if len(args) != 2 :
    print("error")
else :
    print("Ok")
    path = args[1]

#引数のファイルを元に中間コード生成
with open(path) as f :
    s = f.read()
    mid_code = midconverter.generate_code(s)


#run.pyの生成
run_py_code.append(code_pattern.run_py_head)
fndef_code = converter.generate_code(mid_code)

for data in data_holder :
    run_py_code.append(f"{data} = np.array({data},dtype=np.float32)")    

run_py_code.append(code_pattern.run_py_mid1)

for data in data_holder :
    run_py_code.append(f"{data}_symbol = runner.get_id('{data}')")

run_py_code.append("result_symbol = runner.get_id('result')")
run_py_code.append(code_pattern.run_py_mid2)

for data in data_holder:
    code = f"""runner.memcpy_h2d({data}_symbol, {data}, 0, 0, width, height, {length_holder[data]}, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
  """
    run_py_code.append(code)

run_py_code.append(code_pattern.run_py_launch)

run_py_code.append(f"result = np.zeros([{length}], dtype=np.float32)")
number = int (int(length) / (width * height))
code = f"""
runner.memcpy_d2h(result, result_symbol, 0, 0, width, height, {number}, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)"""
run_py_code.append(code)

run_py_code.append(code_pattern.run_py_tail)

run_py_code = "\n".join(run_py_code)

with open('run.py',mode = 'w') as f:
    f.write(run_py_code)

#layout.cslの生成
layout_code.append(code_pattern.layout_head)

for data in data_holder :
    layout_code.append(f"  @export_name(\"{data}\", [*]f32, true);")

layout_code.append(code_pattern.layout_tail)

layout_code = "\n".join(layout_code)

with open('layout.csl',mode = 'w') as f:
    f.write(layout_code)

#pe_program.cslの生成
pe_program_code.append(code_pattern.pe_program_head)

bind_code =[] #タスクバインドを記述するコード
bind_code.append("comptime{")

mainfn_code = [] #main関数を記述するコード
mainfn_code.append(code_pattern.pe_program_main)

#データおよびそのポインタの初期化、dsdの定義、データのエクスポートをまとめて行う
for data in data_holder:
    code = f"""var {data}: [{length_holder[data]}] f32;
var {data}_ptr: [*] f32 = &{data};
var {data}_dsd = @get_dsd(mem1d_dsd, .{{ .tensor_access = |i|{{{length_holder[data]}}} -> {data}[i] }});
"""
    pe_program_code.append(code)
    
    bind_code.append(f"    @export_symbol({data}_ptr, \"{data}\");")

pe_program_code.append(f"var result: [{number}] f32;")
pe_program_code.append("""var result_ptr: [*] f32 = &result;
""")
bind_code.append("    @export_symbol(result_ptr, \"result\");")
bind_code.append("    @export_symbol(main);")

#配列の初期化、dsdの定義
for arr in array_holder :
    code = f"""var {arr} = @zeros([{length_holder[arr]}] f32);
var {arr}_dsd = @get_dsd(mem1d_dsd, .{{ .tensor_access = |i|{{{length_holder[arr]}}} -> {arr}[i] }});
"""
    pe_program_code.append(code)

#変数の初期化
for val in val_holder:
    pe_program_code.append(f"var {val} : f32;")
    mainfn_code.append(f"    {val} = 0.0;")

pe_program_code.append("")

mainfn_code.append(f"""
    @activate({task_schedule[0]}_id);
}}
""")

def num_check (x):
    if x == 21:
        return x+1
    return x
    
even_reduce = False
task_num = 9
#タスクidの定義
for task in task_schedule:

    if task == "reduce":
        if even_reduce :
            continue
        else :
            task_num = num_check(task_num)
            pe_program_code.append(f"const reduce_id:                local_task_id = @get_local_task_id({task_num});")
            task_num += 1
            task_num = num_check(task_num)
            pe_program_code.append(f"const reduce_y_id:              local_task_id = @get_local_task_id({task_num});")
            task_num += 1
            task_num = num_check(task_num)
            pe_program_code.append(f"const bcas_x_id:                local_task_id = @get_local_task_id({task_num});")
            task_num += 1
            task_num = num_check(task_num)
            pe_program_code.append(f"const bcas_y_id:                local_task_id = @get_local_task_id({task_num});")
            task_num += 1
            task_num = num_check(task_num)
            pe_program_code.append(f"const assign_id:                local_task_id = @get_local_task_id({task_num});")
            task_num += 1
            bind_code.append("""    @bind_local_task(reduce, reduce_id);
    @bind_local_task(reduce_y, reduce_y_id);
    @bind_local_task(bcas_x, bcas_x_id);
    @bind_local_task(bcas_y, bcas_y_id);
    @bind_local_task(assign, assign_id);""")
            even_reduce = True
    
    elif task == "exit" :
        task_num = num_check(task_num)
        pe_program_code.append(f"const exit_id:                  local_task_id = @get_local_task_id({task_num});")
        bind_code.append("    @bind_local_task(exit, exit_id);")
        task_num += 1
    
    else :
        task_num = num_check(task_num)
        pe_program_code.append(f"const {task}_id:                local_task_id = @get_local_task_id({task_num});")
        bind_code.append(f"    @bind_local_task({task}, {task}_id);")
        task_num += 1

bind_code.append("}")


pe_program_code.append("\n".join(mainfn_code))
pe_program_code.append(fndef_code)

reduce_code = []  #reduceの処理を記述
reduce_code.append(code_pattern.pe_program_reduce_head)

#reduce

if even_reduce :
    reduce_num = 1
    for data in reduce_da_holder:
        if reduce_num == 1:
            code = f"""
    if (re_count == 1){{
        for ({data}) |data|{{
            tmp += data;
        }}
    }}"""
            reduce_code.append(code)

        else :
            code = f"""    else if (re_count == {reduce_num}){{
        for ({data}) |data|{{
            tmp += data;
        }}
    }}"""
            reduce_code.append(code)
        
        reduce_num += 1

    reduce_code.append(code_pattern.pe_program_reduce_mid)

    reduce_num = 1
    for task in af_reduce :
        if reduce_num == 1:
            code = f"""
    if (re_count == 1){{
        re_count += 1;
        @activate({task}_id);
    }}"""
            reduce_code.append(code)
        
        else :
            code = f"""    else if(re_count == {reduce_num}){{
        re_count += 1;
        @activate({task}_id);
    }}"""
            reduce_code.append(code)
        
        reduce_num += 1
    
    reduce_code.append("""}
""")
    pe_program_code.append("\n".join(reduce_code))

event_code = []  #イベントの内容を記述する
event_num = 1

#event
for event in event_holder :
    event_code.append(f"""task event{event_num}() void{{
""")
    for elem in event :
        event_code.append(f"    {elem}")
    event_code.append(f"""
    @activate({no_af_reduce[event_num]}_id);
}}
""")
    event_num += 1

pe_program_code.append("\n".join(event_code))

exit_code = []

#exit
exit_code.append("task exit() void {")

if print_type == "list":

    code = f"""
    for (@range(u16, {length_holder[print_val]})) |i|{{
        result[i] = {print_val}[i];
    }}"""

    exit_code.append(code)

else :

    code = f"""
    if(px == 0){{
        if(py == 0){{
            result[0] = {print_val};
        }}
    }}"""
    
    exit_code.append(code)

exit_code.append("""
    sys_mod.unblock_cmd_stream();
}
""")

pe_program_code.append("\n".join(exit_code))
pe_program_code.append("\n".join(bind_code))
pe_program_code = "\n".join(pe_program_code)

with open('pe_program.csl',mode = 'w') as f:
    f.write(pe_program_code)

#commands.shの処理
commands_code.append(code_pattern.commands_head)

dim_w = width + 10
dim_h = height + 10

commands_code.append(f"cslc ./layout.csl --fabric-dims={dim_w},{dim_h} \\")
commands_code.append(f"--fabric-offsets=4,1 --params=WIDTH:{width},HEIGHT:{height} -o out --memcpy --channels 1")
commands_code.append("cs_python run.py --name out")
commands_code = "\n".join(commands_code)

with open('commands.sh',mode = 'w') as f:
    f.write(commands_code)
