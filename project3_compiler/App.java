import java.io.*;
import java.util.*;

public class App {

    BufferedReader source;      /* 入力ファイル */
    int line_number;            /* 行番号 */
    char ch;                    /* 先読みの文字 */
    String id_string;           /* 識別子の綴りの文字列 */
    int literal_value;          /* 数（整数）の値 */
    final int Stack_Size = 100;
    int memory_size;
    int memory[];
    int sp, ic;
    Deque<Integer>breaklist = new ArrayDeque<>();
    int de = 0;
    int br_num[] = new int [10]; 

    enum token {
        END_PROGRAM,
        IDENTIFIER, LITERAL,
        ELSE, IF, WHILE,
        COMMA, SEMICOLON,
        LEFT_BRACE, RIGHT_BRACE, LEFT_PAREN, RIGHT_PAREN,
        EQUAL, OROR, ANDAND, OR, AND,
        EQEQ, NOTEQ, LE, LT, GE, GT,
        PLUS, MINUS, STAR, SLASH, PERCENT,
        BREAK,
    }

    token sy;

    enum type {
        Variable, Function
    };

    class id_record {
        type id_class;       /* 変数か関数かの区別 */
        int address;         /* （変数の場合のみ）変数のアドレス */
        int function_id;     /* （関数の場合のみ）関数の識別番号 */
        int parameter_count; /* （関数の場合のみ）引数の個数 */

        id_record(type a, int b, int c, int d) { /* コンストラクタ */
            this.id_class = a;
            this.address = b;
            this.function_id = c;
            this.parameter_count = d;
        }
    }

    Map<String, id_record> symbol_table;
    int variable_count;

    enum operation {
        LCONST, LOAD, STORE, POPUP,
        CALL, JUMP, FJUMP, TJUMP, HALT,
        MULT, DIV, MOD, ADD, SUB, ANDOP, OROP,
        EQOP, NEOP, LEOP, LTOP, GEOP, GTOP
    };

    class code_type {
        operation op_code;
        int operand;
    };

    final int CODE_MAX = 5000;
    int pc = 0;
    code_type code[] = new code_type[CODE_MAX];

    void init_symbol_table() {
        symbol_table = new TreeMap<String, id_record>();
        variable_count = 0;
        symbol_table.put("getd", new id_record(type.Function, -1, 0, 0));
        symbol_table.put("putd", new id_record(type.Function, -1, 1, 2));
        symbol_table.put("newline", new id_record(type.Function, -1, 2, 0));
        symbol_table.put("putchar", new id_record(type.Function, -1, 3, 1));
    }

    void emit(operation op, int param) {
        if (pc >= CODE_MAX) {
            error("code is too long");
            System.exit(1);
        }
        code[pc] = new code_type();
        code[pc].op_code = op;
        code[pc].operand = param;
        pc++;
    }

    id_record search(String name) {

        if (symbol_table.get(name) == null) {
            symbol_table.put(name, new id_record(type.Variable, variable_count, -1, -1));
            variable_count++;
        }

        return symbol_table.get(name);
    }

    id_record lookup_variable(String name) {
        id_record val = search(name);

        if (val.id_class != type.Variable) {
            error("variable is predicted, but the function");
        }

        return val;
    }

    id_record lookup_function(String name) {
        id_record fnc = search(name);

        if (fnc.id_class != type.Function) {
            error("function is predicted, but the variable");
        }

        return fnc;
    }

    public static void main(String[] args) throws Exception {

        App App_instance = new App();
        App_instance.driver(args);
    }

    void driver(String[] args) throws Exception {

        if (args.length == 1) {
            source = new BufferedReader(new FileReader(new File(args[0])));
        } else {
            source = new BufferedReader(new InputStreamReader(System.in));
            if (args.length != 0) {
                error("multiple source file is not supported");
            }
        }

        line_number = 1;
        ch = ' ';

        init_symbol_table();
        get_token();
        statement();
        emit(operation.HALT, 0);
        memory_size = variable_count + Stack_Size;
        memory = new int[memory_size];
        //print_code();
        interpret(false);
        if (sy != token.END_PROGRAM) {
            error("extra text at the end of the program");
            System.out.println(sy);
        }
    }

    void error(String s) {
        System.out.println(String.format("%4d", line_number) + ": " + s);
    }

    void print_code() {
        for (int i = 0; i < pc; i++)
            System.out.println(String.format("%5d", i) + ": " +
                    String.format("%-6s", code[i].op_code) +
                    String.format("%6d", code[i].operand));
    }

    void next_ch() {

        try {
            ch = (char) source.read();
            if (ch == '\n')
                line_number++;
        } catch (Exception e) {
            System.out.println("IO error occurred");
            System.exit(1);
        }
    }

    void get_token() {

        // 空白等を読み飛ばし
        while (ch == ' ' || ch == '\n' || ch == '\r' || ch == '\t') {
            next_ch();
        }

        // プログラムの終了
        if (ch == 65535) {
            sy = token.END_PROGRAM;
            return;
        }

        // 識別子の読み込み
        if ((ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z') || ch == '_') {
            id_string = "";

            while ((ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z') || ch == '_'
                    || (ch >= '0' && ch <= '9')) {
                id_string += ch;
                next_ch();
            }

            if (id_string.equals("else")) {
                sy = token.ELSE;
                return;
            }
            if (id_string.equals("if")) {
                sy = token.IF;
                return;
            }
            if (id_string.equals("while")) {
                sy = token.WHILE;
                return;
            }
            if (id_string.equals("break")){
                sy = token.BREAK;
                return;
            }

            sy = token.IDENTIFIER;
            return;
        }

        // 数の読みこみ
        if (ch >= '0' && ch <= '9') {
            int v = 0;
            long long_v = 0;
            boolean is_over = false;

            while (ch >= '0' && ch <= '9') {
                int ch_num = ch - '0';
                v = v * 10 + ch_num;
                long_v = long_v * 10 + ch_num;

                if (!(is_over)) {
                    if (long_v > 2147483647) {
                        is_over = true;
                    }
                }
                next_ch();
            }

            if (is_over) {
                error("value is overflowing");
                literal_value = 0;
                sy = token.LITERAL;
                return;
            }
            literal_value = v;
            sy = token.LITERAL;
            return;
        }

        // 1文字の記号読み込み
        if (ch == ',') {
            next_ch();
            sy = token.COMMA;
            return;
        }
        if (ch == ';') {
            next_ch();
            sy = token.SEMICOLON;
            return;
        }
        if (ch == '{') {
            next_ch();
            sy = token.LEFT_BRACE;
            return;
        }
        if (ch == '}') {
            next_ch();
            sy = token.RIGHT_BRACE;
            return;
        }
        if (ch == '(') {
            next_ch();
            sy = token.LEFT_PAREN;
            return;
        }
        if (ch == ')') {
            next_ch();
            sy = token.RIGHT_PAREN;
            return;
        }
        if (ch == '+') {
            next_ch();
            sy = token.PLUS;
            return;
        }
        if (ch == '-') {
            next_ch();
            sy = token.MINUS;
            return;
        }
        if (ch == '*') {
            next_ch();
            sy = token.STAR;
            return;
        }

        if (ch == '%') {
            next_ch();
            sy = token.PERCENT;
            return;
        }

        // 2文字の記号読み込み
        if (ch == '&') {
            next_ch();
            if (ch == '&') {
                next_ch();
                sy = token.ANDAND;
                return;
            }
            sy = token.AND;
            return;
        }
        if (ch == '=') {
            next_ch();
            if (ch == '=') {
                next_ch();
                sy = token.EQEQ;
                return;
            }
            sy = token.EQUAL;
            return;
        }

        if (ch == '!') {
            next_ch();
            if (ch == '=') {
                next_ch();
                sy = token.NOTEQ;
                return;
            } else {
                error("exclamation is only supported for equal");
                get_token();
                return;
            }
        }

        if (ch == '<') {
            next_ch();
            if (ch == '=') {
                next_ch();
                sy = token.LE;
                return;
            }
            sy = token.LT;
            return;
        }
        if (ch == '>') {
            next_ch();
            if (ch == '=') {
                next_ch();
                sy = token.GE;
                return;
            }
            sy = token.GT;
            return;
        }
        if (ch == '|') {
            next_ch();
            if (ch == '|') {
                next_ch();
                sy = token.OROR;
                return;
            }
            sy = token.OR;
            return;
        }

        // コメントの読み飛ばし
        if (ch == '/') {
            next_ch();

            // コメント用
            if (ch == '*') {
                next_ch();
                char before_ch = ch;
                while (true) {
                    next_ch();
                    if (before_ch == '*' && ch == '/') {
                        next_ch();
                        get_token();
                        return;
                    }
                    if (ch == 65535) {
                        error("comments not closed");
                        sy = token.END_PROGRAM;
                        return;
                    }
                    before_ch = ch;
                }
            }

            sy = token.SLASH;
            return;
        }

        error("unrecognized character");
        next_ch();
        get_token();
        return;
    }

    // 逆ポーランド記法でのデバッグ用
    final boolean debug_parse = false;

    void polish(String s) {
        if (debug_parse)
            System.out.print(s + " ");
    }

    void polish_newline() {
        if (debug_parse)
            System.out.println();
    }

    // 1次式
    void primary_expression() {

        if (sy == token.LITERAL) {
            polish(literal_value + "");
            emit(operation.LCONST, literal_value);
            get_token();
        } else if (sy == token.IDENTIFIER) {
            get_token();

            if (sy == token.LEFT_PAREN) {
                polish(id_string + "");
                id_record tmp = lookup_function(id_string);
                int call_count = 0;
                get_token();

                if (sy != token.RIGHT_PAREN) {
                    expression();
                    call_count++;
                    while (sy == token.COMMA) {
                        get_token();
                        expression();
                        call_count++;
                    }
                }

                if (tmp.parameter_count != call_count) {
                    error("parameter not match");
                }
                polish("call-" + call_count);
                emit(operation.CALL, tmp.function_id);
                if (sy == token.END_PROGRAM) {
                    error("syntax error");
                } else if (sy != token.RIGHT_PAREN) {
                    error("syntax error");
                    get_token();
                } else {
                    get_token();
                }
            } else {
                polish(id_string + "");
                id_record tmp = lookup_variable(id_string);
                emit(operation.LOAD, tmp.address);
            }
        } else if (sy == token.LEFT_PAREN) {
            get_token();
            expression();
            if (sy == token.RIGHT_PAREN)
                get_token();
            else
                error("right parenthesis expected");
        } else {
            error("unrecognized element in expression");
            get_token();
        }
    }

    // 単項式
    void unary_expression() {

        if (sy == token.MINUS) {
            get_token();
            emit(operation.LCONST, 0);
            unary_expression();
            polish("u-");
            emit(operation.SUB, 0);
        } else {
            primary_expression();
        }
    }

    // 乗除式
    void multiplicative_expression() {
        unary_expression();
        while (sy == token.STAR || sy == token.SLASH || sy == token.PERCENT) {

            String tmp_sy = "";
            operation tmp_op;
            if (sy == token.STAR) {
                tmp_sy = "*";
                tmp_op = operation.MULT;
            } else if (sy == token.SLASH) {
                tmp_sy = "/";
                tmp_op = operation.DIV;
            } else {
                tmp_sy = "%";
                tmp_op = operation.MOD;
            }
            get_token();
            unary_expression();
            polish(tmp_sy);
            emit(tmp_op, 0);
        }
    }

    // 加減式
    void additive_expression() {
        multiplicative_expression();
        while (sy == token.PLUS || sy == token.MINUS) {

            String tmp_sy = "";
            operation tmp_op;
            if (sy == token.PLUS) {
                tmp_sy = "+";
                tmp_op = operation.ADD;
            } else {
                tmp_sy = "-";
                tmp_op = operation.SUB;
            }
            get_token();
            multiplicative_expression();
            polish(tmp_sy);
            emit(tmp_op, 0);
        }
    }

    // 関係式
    void relational_expression() {
        additive_expression();
        while (sy == token.LE || sy == token.LT || sy == token.GE || sy == token.GT) {

            String tmp_sy = "";
            operation tmp_op;
            if (sy == token.LE) {
                tmp_sy = "<=";
                tmp_op = operation.LEOP;
            } else if (sy == token.LT) {
                tmp_sy = "<";
                tmp_op = operation.LTOP;
            } else if (sy == token.GE) {
                tmp_sy = ">=";
                tmp_op = operation.GEOP;
            } else {
                tmp_sy = ">";
                tmp_op = operation.GTOP;
            }

            get_token();
            additive_expression();
            polish(tmp_sy);
            emit(tmp_op, 0);
        }
    }

    // 等価式
    void equality_expression() {
        relational_expression();
        while (sy == token.EQEQ || sy == token.NOTEQ) {

            String tmp_sy = "";
            operation tmp_op;
            if (sy == token.EQEQ) {
                tmp_sy = "==";
                tmp_op = operation.EQOP;
            } else {
                tmp_sy = "!=";
                tmp_op = operation.NEOP;
            }
            get_token();
            relational_expression();
            polish(tmp_sy);
            emit(tmp_op, 0);
        }
    }

    // ビットAND式
    void bit_and_expression() {
        equality_expression();
        while (sy == token.AND) {
            get_token();
            equality_expression();
            polish("&");
            emit(operation.ANDOP, 0);
        }
    }

    // ビットOR式
    void bit_or_expression() {
        bit_and_expression();
        while (sy == token.OR) {
            get_token();
            bit_and_expression();
            polish("|");
            emit(operation.OROP, 0);
        }
    }

    // 論理AND式
    void logical_and_expression() {
        bit_or_expression();
        while (sy == token.ANDAND) {
            int pc_save = pc;
            emit(operation.FJUMP, 0);
            get_token();
            bit_or_expression();
            polish("&&");
            emit(operation.FJUMP, pc + 3);
            emit(operation.LCONST, 1);
            emit(operation.JUMP, pc + 2);
            emit(operation.LCONST, 0);
            code[pc_save].operand = pc - 1;
        }
    }

    // 論理OR式
    void logical_or_expression() {
        logical_and_expression();
        while (sy == token.OROR) {
            int pc_save = pc;
            emit(operation.TJUMP, 0);
            get_token();
            logical_and_expression();
            polish("||");
            emit(operation.TJUMP, pc + 3);
            emit(operation.LCONST, 0);
            emit(operation.JUMP, pc + 2);
            emit(operation.LCONST, 1);
            code[pc_save].operand = pc - 1;
        }
    }

    // 式
    void expression() {
        logical_or_expression();
        if (sy == token.EQUAL) {
            if (code[pc - 1].op_code != operation.LOAD)
                error("assignment to non-variable");
            pc--;
            int tmp = code[pc].operand;
            get_token();
            expression();
            polish("=");
            emit(operation.STORE, tmp);
        }
    }

    // 文
    void statement() {
        // System.out.println("statement(): token = " + sy);
        if (sy == token.SEMICOLON) {
            polish("empty statement");
            polish_newline();
            get_token();
        } else if (sy == token.IF) {
            polish("if statement: ");
            get_token();

            // 条件式
            if (sy == token.LEFT_PAREN) {
                get_token();
                expression();
                polish_newline();
                if (sy != token.RIGHT_PAREN) {
                    error("missing ) after if condition");
                }
                get_token();
            } else {
                error("if syntax error");
            }

            int pc_save = pc;
            emit(operation.FJUMP, 0);

            // trueの文
            if (sy == token.LEFT_BRACE) {
                get_token();
                while (sy != token.RIGHT_BRACE) {
                    polish("  ");
                    statement();
                }
                if (sy == token.RIGHT_BRACE) {
                    get_token();
                } else {
                    error("missing } after if block");
                }
            } else {
                polish("  ");
                statement();
            }

            if (sy == token.ELSE) {
                polish("else part");
                polish_newline();
                get_token();

                int else_jump = pc;
                emit(operation.JUMP, 0);
                code[pc_save].operand = pc;

                if (sy == token.LEFT_BRACE) {
                    get_token();
                    while (sy != token.RIGHT_BRACE) {
                        polish("  ");
                        statement();
                    }
                    if (sy == token.RIGHT_BRACE) {
                        get_token();
                    } else {
                        error("missing } after else block");
                    }
                } else {
                    polish(("  "));
                    statement();
                }

                code[else_jump].operand = pc;
            } else {
                code[pc_save].operand = pc;
            }

            polish("end if statement");
            polish_newline();
        } else if (sy == token.WHILE) {
            polish("while statement: ");
            get_token();

            int while_start = pc;
            de ++;
            br_num[de] = 0;

            // 条件式
            if (sy == token.LEFT_PAREN) {
                get_token();
                expression();
                polish_newline();
                if (sy != token.RIGHT_PAREN) {
                    error("missing ) after while condition");
                }
                get_token();
            } else {
                error("while syntax error");
            }

            int pc_save = pc;
            emit(operation.FJUMP, 0);

            // ループされる文
            if (sy == token.LEFT_BRACE) {
                get_token();
                while (sy != token.RIGHT_BRACE) {
                    polish("  ");
                    statement();
                }
                if (sy == token.RIGHT_BRACE) {
                    get_token();
                } else {
                    error("missing } after while block");
                }
            } else {
                polish("  ");
                statement();
            }

            emit(operation.JUMP, while_start);
            code[pc_save].operand = pc;

            int i;
            for(i=0;i<br_num[de];i++){
                code[breaklist.pop()].operand =pc; 
            }
            polish("end while statement");
            polish_newline();
            de--;

        } else if (sy == token.LEFT_BRACE) {
            get_token();
            while (sy != token.RIGHT_BRACE && sy != token.END_PROGRAM) {
                statement();
            }
            if (sy == token.RIGHT_BRACE) {
                get_token();
            } else {
                error("syntax error1");
            }
        }else if (sy == token.BREAK){
            if(de == 0){
                error("break out of while");
            }
            breaklist.push(pc);
            emit(operation.JUMP, 0);
            br_num[de]++;
            get_token();
        } 
        else {
            expression();
            polish_newline();
            if (sy == token.SEMICOLON) {
                get_token();
            } else {
                error("syntax error2");
                get_token();
            }
            emit(operation.POPUP, 0);
        }
    }

    void interpret(boolean trace) {
        Scanner sc = new Scanner(System.in);
        ic = 0;
        sp = variable_count;
        for (;;) {
            operation instruction = code[ic].op_code;
            int argument = code[ic].operand;
            if (trace) {
                System.out.print("ic=" + String.format("%4d", ic) +
                        ", sp=" + String.format("%5d", sp) +
                        ", code=(" +
                        String.format("%-6s", instruction) +
                        String.format("%6d", argument) + ")");
                if (sp > variable_count) {
                    int val = pop();
                    push(val);
                    System.out.print(", top=" + String.format("%10d", val));
                }
                System.out.println();
            }
            ic++;

            int r, l;
            switch (instruction) {
                case LCONST:
                    push(argument);
                    continue;
                case LOAD:
                    if (argument < 0 || argument > variable_count) {
                        run_error("references beyond address");
                    } else {
                        push(memory[argument]);
                    }
                    continue;
                case STORE:
                    int tmp;
                    tmp = pop();
                    if (argument < 0 || argument > variable_count) {
                        run_error("references beyond address");
                    } else {
                        memory[argument] = tmp;
                        push(tmp);
                    }
                    continue;
                case POPUP:
                    pop();
                    continue;
                case CALL:
                    if (argument == 0) {
                        System.out.print("getd: ");
                        push(sc.nextInt());
                    } else if (argument == 1) {
                        int width = pop();
                        int val = pop();
                        String s = String.format("%d", val);
                        int d = width - s.length();
                        while (d > 0) {
                            System.out.print(" ");
                            d--;
                        }
                        System.out.print(s);
                        push(val);
                    } else if (argument == 2) {
                        System.out.println();
                        push(0);
                    } else if (argument == 3) {
                        int val = pop();
                        char c = (char) val;
                        System.out.print(c);
                        push(val);
                    }
                    continue;
                case JUMP:
                    ic = argument;
                    continue;
                case FJUMP:
                    if (pop() == 0) {
                        ic = argument;
                    }
                    continue;
                case TJUMP:
                    if (pop() != 0) {
                        ic = argument;
                    }
                    continue;
                case HALT:
                    if (sp != variable_count) {
                        run_error("interpret bug");
                    }
                    return;
                case ADD:
                    push(pop() + pop());
                    continue;
                case SUB:
                    r = pop();
                    l = pop();
                    push(l - r);
                    continue;
                case MULT:
                    push(pop() * pop());
                    continue;
                case ANDOP:
                    push(pop() & pop());
                    continue;
                case OROP:
                    push(pop() | pop());
                    continue;
                case DIV:
                    r = pop();
                    l = pop();
                    if (r == 0) {
                        run_error("0 div");
                    }
                    push(l / r);
                    continue;
                case MOD:
                    r = pop();
                    l = pop();
                    if (r == 0) {
                        run_error("0 div");
                    }
                    push(l % r);
                    continue;
                case EQOP:
                    r = pop();
                    l = pop();
                    if (l == r) {
                        push(1);
                    } else {
                        push(0);
                    }
                    continue;
                case NEOP:
                    r = pop();
                    l = pop();
                    if (l != r) {
                        push(1);
                    } else {
                        push(0);
                    }
                    continue;
                case LEOP:
                    r = pop();
                    l = pop();
                    if (l <= r) {
                        push(1);
                    } else {
                        push(0);
                    }
                    continue;
                case LTOP:
                    r = pop();
                    l = pop();
                    if (l < r) {
                        push(1);
                    } else {
                        push(0);
                    }
                    continue;
                case GEOP:
                    r = pop();
                    l = pop();
                    if (l >= r) {
                        push(1);
                    } else {
                        push(0);
                    }
                    continue;
                case GTOP:
                    r = pop();
                    l = pop();
                    if (l > r) {
                        push(1);
                    } else {
                        push(0);
                    }
                    continue;
                default:
                    run_error("system error: undefined op code");
            }
        }
    }

    void push(int x) {
        if (sp >= memory_size)
            run_error("stack overflow");
        memory[sp] = x;
        sp++;
    }

    int pop() {
        if (sp <= variable_count)
            run_error("system error: stack underflow");
        sp--;
        return (memory[sp]);
    }

    void run_error(String s) {
        System.out.println(s);
        System.exit(1);
    }
}
