"""Author ordinary structured Adva syntax; never specialize in this host code.

The generated mix walks static data, emits its literal-construction instructions,
then binds input and relocates branches in an arbitrary admitted v1 body.
Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.bounded_self_compiler.language import SOURCE, prim, seq, if_, while_, seed_compile, encode_source

NAMES = [
    ('work','stack'), ('output','stack'), ('declarations','stack'),
    *[(n,'data') for n in ('bundle','q','name','decls','code','static','frame','item','tmp',
        'a','b','c','child','depth_box','parent_box','child_box','dyn_box','bound_box',
        'int_box','data_box','text','empty')],
    *[(n,'integer') for n in ('zero','one','minus','nregs','base','depth','child_depth',
        'tag','index','length','offset','number','probe')],
    ('flag','boolean'), ('test','boolean'), ('more','boolean')
]
R = {n:i for i,(n,_) in enumerate(NAMES)}


def op(code, **kw):
    return prim(code, **{k: (R[v] if isinstance(v,str) and k != 'reason' else
                            [R[x] for x in v] if isinstance(v,list) else v) for k,v in kw.items()})
def c(dst, value): return op('constant',dst=dst,value=value)
def eq(left,right,dst='test'): return op('equal',left=left,right=right,dst=dst)
def plus(left,right,dst): return op('add',left=left,right=right,dst=dst)
def field(src,index,dst,arity): return op('field',src=src,index=index,dst=dst,arity=arity)
def box(src,dst): return op('box_integer',src=src,dst=dst)
def push(stack,src): return op('push',stack=stack,src=src)
def emit(tag, fields):
    return seq(op('node',tag=tag,fields=fields,dst='tmp'),push('output','tmp'))
def ne(left,right,dst):
    return seq(eq(left,right,dst),if_(R[dst],eq('zero','one',dst),eq('zero','zero',dst)))
def nonempty(stack,flag):
    return seq(op('is_empty',stack=stack,dst=flag),
               if_(R[flag],eq('zero','one',flag),eq('zero','zero',flag)))
def check_tag(src,tag):
    return seq(op('tag',src=src,dst='tag'),c('probe',tag),eq('tag','probe'),
               if_(R['test'],seq(),op('reject',reason='mix input tag')))
def scheduled(item, depth, finish=False):
    return seq(op('node',tag=1 if finish else 0,fields=[item,depth],dst='tmp'),push('work','tmp'))


def source():
    # Append sixteen fixed, reserved scratch declarations to the original file.
    # Reuse the future scratch-index boxes for the ASCII prefix before assigning
    # their index values. Generate mix_A through mix_P in one ordinary loop.
    declare=[]
    for byte,reg in zip(b'mix_',('dyn_box','bound_box','int_box','data_box')):
        declare += [c('number',byte),box('number',reg)]
    kind=op('node',tag=3,fields=['text'],dst='tmp')
    for index,tag in reversed(list(enumerate([2,2,0,2]))):
        kind=seq(c('probe',index),eq('index','probe'),
                 if_(R['test'],op('node',tag=tag,fields=['text'],dst='tmp'),kind))
    declare += [c('index',0),c('length',16),ne('index','length','flag'),
        while_(R['flag'],seq(c('number',65),plus('number','index','number'),box('number','a'),
            op('node',tag=255,fields=['dyn_box','bound_box','int_box','data_box','a'],dst='text'),
            kind,push('work','tmp'),plus('index','one','index'),ne('index','length','flag')))]
    # Work holds the declaration vector until it is packed, then becomes DFS work.
    init=seq(c('zero',0),c('one',1),c('minus',-1),op('input',dst='bundle'),check_tag('bundle',42),
        field('bundle',0,'q',2),field('bundle',1,'static',2),check_tag('q',241),
        field('q',0,'name',3),field('q',1,'decls',3),field('q',2,'code',3),
        op('length',src='decls',dst='nregs'),c('index',0),op('clear',stack='work'),
        ne('index','nregs','flag'),while_(R['flag'],seq(
            op('field_dynamic',src='decls',index='index',dst='tmp'),push('work','tmp'),
            plus('index','one','index'),ne('index','nregs','flag'))),
        *declare,op('pack',stack='work',tag=254,dst='decls'),op('clear',stack='work'),
        box('nregs','dyn_box'),plus('nregs','one','number'),box('number','bound_box'),
        plus('number','one','number'),box('number','int_box'),plus('number','one','number'),box('number','data_box'),
        plus('number','one','base'),box('base','parent_box'),op('clear',stack='output'),
        emit(0,['dyn_box']),emit(3,['parent_box']),box('zero','depth_box'),scheduled('static','depth_box'))
    leaf=seq(emit(1,['int_box','item']),emit(10,['int_box','data_box']),emit(4,['parent_box','data_box']))
    node=seq(plus('depth','one','child_depth'),c('probe',12),eq('child_depth','probe'),
        if_(R['test'],op('reject',reason='mix static literal depth'),seq()),
        box('child_depth','c'),plus('base','child_depth','number'),box('number','child_box'),
        emit(3,['child_box']),box('tag','a'),scheduled('a','depth_box',True),
        op('length',src='item',dst='index'),ne('index','zero','more'),
        while_(R['more'],seq(plus('index','minus','index'),
            op('field_dynamic',src='item',index='index',dst='child'),scheduled('child','c'),
            ne('index','zero','more'))))
    finish=seq(plus('depth','one','child_depth'),plus('base','child_depth','number'),
        box('number','child_box'),emit(21,['child_box','item','data_box']),emit(4,['parent_box','data_box']))
    walk=seq(nonempty('work','flag'),while_(R['flag'],seq(op('pop',stack='work',dst='frame'),
        op('tag',src='frame',dst='tag'),field('frame',0,'item',2),field('frame',1,'depth_box',2),
        op('as_integer',src='depth_box',dst='depth'),plus('base','depth','number'),box('number','parent_box'),
        eq('tag','zero'),if_(R['test'],seq(op('tag',src='item',dst='tag'),eq('tag','minus'),
            if_(R['test'],leaf,node)),finish),nonempty('work','flag'))))
    prefix_end=seq(box('base','parent_box'),emit(5,['parent_box','data_box']),
        c('number',42),box('number','a'),op('node',tag=254,fields=['data_box','dyn_box'],dst='b'),
        emit(11,['a','b','bound_box']),op('stack_length',stack='output',dst='offset'))
    relocate_jump=seq(field('item',0,'a',1),op('as_integer',src='a',dst='number'),
        plus('number','offset','number'),box('number','a'),emit(15,['a']))
    relocate_branch=seq(field('item',0,'a',3),field('item',1,'b',3),field('item',2,'c',3),
        op('as_integer',src='b',dst='number'),plus('number','offset','number'),box('number','b'),
        op('as_integer',src='c',dst='number'),plus('number','offset','number'),box('number','c'),emit(16,['a','b','c']))
    copy_body=seq(op('length',src='code',dst='length'),c('index',0),ne('index','length','flag'),
        while_(R['flag'],seq(op('field_dynamic',src='code',index='index',dst='item'),
            op('tag',src='item',dst='tag'),eq('tag','zero'),
            if_(R['test'],seq(field('item',0,'a',1),emit(2,['bound_box','a'])),
                seq(c('probe',15),eq('tag','probe'),if_(R['test'],relocate_jump,
                    seq(c('probe',16),eq('tag','probe'),if_(R['test'],relocate_branch,push('output','item')))))),
            plus('index','one','index'),ne('index','length','flag'))),
        op('pack',stack='output',tag=250,dst='tmp'),
        op('node',tag=241,fields=['name','decls','tmp'],dst='tmp'),op('return',src='tmp'))
    return {'schema':SOURCE,'name':'bounded-input-binding-mix',
            'registers':[{'name':n,'kind':k} for n,k in NAMES],
            'body':seq(init,walk,prefix_end,copy_body)}


if __name__ == '__main__':
    dest=ROOT/'programs/bounded-mix'
    dest.mkdir(exist_ok=True)
    s=source(); target=seed_compile(s)
    for name,value in [('mix.source.adva',s),('mix.seed.adva',target),('mix.input.json',encode_source(s))]:
        (dest/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({'registers':len(NAMES),'instructions':len(target['code'])}))
