class Const(object):
    workflow_status = {
        'wait': '待人工执行',
        'execute': 'sql执行中',
        'done': '执行完成',
        'stop': '人工终止',
        'reject': '审核不通过',
        'exception': '执行异常',
        'reviewing': '审核中',
        'abort': '取消',
    }