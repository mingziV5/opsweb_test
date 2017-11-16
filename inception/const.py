class Const(object):
    workflow_status = {
        'wait':'待审核',
        'excute':'sql执行中',
        'done':'执行完成',
        'stop':'人工终止',
        'reject':'审核不通过',
        'exception':'执行异常',
        'reviewing':'人工审核中',
    }