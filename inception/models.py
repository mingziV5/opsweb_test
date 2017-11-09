from django.db import models
# Create your models here.
class MasterConfig(models.Model):
    cluster_name = models.CharField('数据库集群名称', max_length=100)
    db_name = models.CharField('数据库名', max_length=100)
    master_host = models.CharField('master主库地址', max_length=200)
    master_port = models.IntegerField('master库端口', default=3306)
    master_user = models.CharField('执行sql账号', max_length=100)
    master_passwd = models.CharField('执行sql密码', max_length=200)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        link_name = self.cluster_name + '_' + self.db_name
        return link_name

class SqlWorkflowStatus(models.Model):
    status_name = models.CharField('工单状态', max_length=50)

class SqlWorkflow(models.Model):
    workflow_name = models.CharField('sql工单名称', max_length=100)
    proposer = models.CharField('申请人', max_length=150)
    reviewer = models.CharField('审核人', max_length=150)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    review_time = models.DateTimeField('审核时间', null=True, blank=True)
    finish_time = models.DateTimeField('结束时间', null=True, blank=True)
    status = models.ForeignKey(SqlWorkflowStatus)
    backup = models.CharField('是否备份', choices=((0, '否'),(1, '是')), max_length=10)
    review_content = models.TextField('自动审核返回的JSON')
    cluster_db_name = models.CharField('执行目标库', max_length=200)
    sql_content = models.TextField('具体执行内容')
    excute_result = models.TextField('执行结果返回的JSON')

    def __str__(self):
        return self.workflow_name