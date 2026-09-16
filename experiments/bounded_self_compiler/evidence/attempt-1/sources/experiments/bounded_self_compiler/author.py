"""Reproducible source authoring only; never called during a native compilation.

The generated compiler.source.adva is the complete executable source. All
traversal, sizing, address calculation and instruction construction below are
ordinary structured Adva syntax, compiled once by the explicit external seed.
"""
import json
from pathlib import Path
from language import SOURCE, prim as p, seq, if_, while_, seed_compile, encode_source

NAMES = [
 ('work','stack'),('output','stack'),('scan','stack'),
 ('module','data'),('name','data'),('decls','data'),('item','data'),
 ('a','data'),('b','data'),('tmp','data'),('scan_item','data'),('child','data'),
 ('boxed_condition','data'),('boxed_yes','data'),('boxed_no','data'),
 ('zero','integer'),('one','integer'),('minus_one','integer'),('two','integer'),
 ('three','integer'),('tag','integer'),('scan_tag','integer'),('index','integer'),
 ('scan_index','integer'),('size','integer'),('first_size','integer'),
 ('pc','integer'),('end','integer'),('else_pc','integer'),
 ('flag','boolean'),('test','boolean'),('scan_flag','boolean'),('scan_test','boolean'),
 ('iter_flag','boolean'),('scan_iter_flag','boolean'),
]
R = {n: i for i,(n,_) in enumerate(NAMES)}
def op(opcode, **args):
    return p(opcode, **{k: R[v] if isinstance(v,str) and k != 'reason' else
                      [R[x] for x in v] if isinstance(v,list) else v for k,v in args.items()})
def c(dst,value): return op('constant',dst=dst,value=value)
def add(left,right,dst): return op('add',left=left,right=right,dst=dst)
def field(src,index,dst,arity): return op('field',src=src,index=index,dst=dst,arity=arity)
def push(stack,src): return op('push',stack=stack,src=src)
def eq(left,right,dst='test'): return op('equal',left=left,right=right,dst=dst)
def nonempty(stack,flag,test):
    return seq(op('is_empty',stack=stack,dst=test),
               if_(R[test],eq('zero','one',flag),eq('zero','zero',flag)))
def reverse_children(src,stack,index,flag,temp):
    return seq(op('length',src=src,dst=index), eq(index,'zero',flag),
               if_(R[flag],eq('zero','one',flag),eq('zero','zero',flag)),
               while_(R[flag],seq(add(index,'minus_one',index),
                   op('field_dynamic',src=src,index=index,dst=temp),push(stack,temp),
                   eq(index,'zero',flag),if_(R[flag],eq('zero','one',flag),eq('zero','zero',flag)))))
def count(src):
    dispatch=if_(R['scan_test'],add('size','one','size'),seq(
        eq('scan_tag','one','scan_test'),
        if_(R['scan_test'],reverse_children('scan_item','scan','scan_index','scan_iter_flag','child'),seq(
            add('size','two','size'),eq('scan_tag','two','scan_test'),
            if_(R['scan_test'],seq(field('scan_item',1,'child',3),push('scan','child'),
                                  field('scan_item',2,'child',3),push('scan','child')),
                seq(eq('scan_tag','three','scan_test'),
                    if_(R['scan_test'],seq(field('scan_item',1,'child',2),push('scan','child')),
                        op('reject',reason='unsupported source tag'))))))))
    return seq(c('size',0),op('clear',stack='scan'),push('scan',src),
               nonempty('scan','scan_flag','scan_test'),
               while_(R['scan_flag'],seq(op('pop',stack='scan',dst='scan_item'),
                    op('tag',src='scan_item',dst='scan_tag'),eq('scan_tag','zero','scan_test'),
                    dispatch,nonempty('scan','scan_flag','scan_test'))))
def emit_branch():
    return seq(op('box_integer',src='pc',dst='boxed_yes'),
               op('box_integer',src='else_pc',dst='boxed_no'),
               op('node',tag=16,fields=['boxed_condition','boxed_yes','boxed_no'],dst='tmp'),push('output','tmp'))
def schedule_jump(target):
    return seq(op('box_integer',src=target,dst='tmp'),
               op('node',tag=15,fields=['tmp'],dst='tmp'),
               op('node',tag=0,fields=['tmp'],dst='tmp'),push('work','tmp'))
def source():
    then_case=seq(field('item',0,'tmp',1),push('output','tmp'))
    if_case=seq(field('item',0,'boxed_condition',3),field('item',1,'a',3),field('item',2,'b',3),
        count('a'),op('copy',src='size',dst='first_size'),count('b'),
        op('stack_length',stack='output',dst='pc'),add('pc','one','pc'),
        add('pc','first_size','else_pc'),add('else_pc','one','else_pc'),add('else_pc','size','end'),
        emit_branch(),push('work','b'),schedule_jump('end'),push('work','a'))
    loop_case=seq(field('item',0,'boxed_condition',2),field('item',1,'a',2),count('a'),
        op('stack_length',stack='output',dst='pc'),op('copy',src='pc',dst='end'),
        add('pc','size','else_pc'),add('else_pc','two','else_pc'),add('pc','one','pc'),
        emit_branch(),schedule_jump('end'),push('work','a'))
    dispatch=if_(R['test'],then_case,seq(eq('tag','one'),
        if_(R['test'],reverse_children('item','work','index','iter_flag','tmp'),seq(eq('tag','two'),
            if_(R['test'],if_case,seq(eq('tag','three'),
                if_(R['test'],loop_case,op('reject',reason='unsupported source tag'))))))))
    body=seq(c('zero',0),c('one',1),c('minus_one',-1),c('two',2),c('three',3),
        op('input',dst='module'),field('module',0,'name',3),field('module',1,'decls',3),
        field('module',2,'item',3),op('clear',stack='work'),op('clear',stack='output'),push('work','item'),
        nonempty('work','flag','test'),while_(R['flag'],seq(op('pop',stack='work',dst='item'),
            op('tag',src='item',dst='tag'),eq('tag','zero'),dispatch,nonempty('work','flag','test'))),
        op('pack',stack='output',tag=250,dst='tmp'),
        op('node',tag=241,fields=['name','decls','tmp'],dst='tmp'),op('return',src='tmp'))
    return {'schema':SOURCE,'name':'structured-self-compiler','registers':[{'name':n,'kind':t} for n,t in NAMES], 'body':body}

if __name__ == '__main__':
    root=Path(__file__).resolve().parents[2]/'programs/bounded-self-compiler'
    s=source()
    for name,value in [('compiler.source.adva',s),('compiler.seed.adva',seed_compile(s)),('compiler.input.json',encode_source(s))]:
        (root/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({'registers':len(s['registers']),'instructions':len(seed_compile(s)['code']),
                      'source_wire_bytes':len(json.dumps(encode_source(s),separators=(',',':')))}))
