import pymysql
from django.conf import settings
from django.db import connection
from django.db.models import Q
from inception.models import MasterConfig
from opsweb.utils import GetLogger

import traceback
import re

class SqlDao(object):
    _chart_days = 90

    #连接指定的mysql实例，获取非系统的database并返回
    def get_db_by_cluster(self, master_host, master_port, master_user, master_pass):
        list_db = []
        conn = None
        cursor = None

        try:
            conn = pymysql.connect(host=master_host, port=master_port, user=master_user, passwd=master_pass, charset='utf8mb4')
            cursor = conn.cursor()
            sql = 'show database'
            n = cursor.execute(sql)
            list_db = [row[0] for row in cursor.fetchall() if
                       row[0] not in (('information_schema', 'performance_schema', 'mysql', 'test', 'sys'))]
        except pymysql.Warning as e:
            GetLogger().get_logger().error(e)
        except pymysql.Error as e:
            GetLogger().get_logger().error(e)
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.commit()
                conn.close()
        return list_db

    #获取指定时间段内工单数量
    def get_work_by_month(self):
        cursor = connection.cursor()
        sql = "select date_format(create_time, '%%m-%%d'),count(1) " \
              "from inception_sqlworkflow " \
              "where create_time>=date_add(now(),interval -%s day) " \
              "group by date_format(create_time, '%%m-%%d') " \
              "order by 1 asc;" %(self._chart_days)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    #在指定时间内按申请人分组统计提交最多的50人
    def get_work_by_person(self):
        cursor = connection.cursor()
        sql = "select proposer, count(*) as cnt " \
              "from inception_sqlworkflow " \
              "where create_time>=date_add(now(),interval -%s day) " \
              "group by proposer " \
              "order by cnt " \
              "desc limit 50;" %(self._chart_days)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

class InceptionDao(object):
    #初始化inception参数
    def __init__(self):
        try:
            self.inception_host = settings.INCEPTION_HOST
            self.inception_port = int(settings.INCEPTION_PORT)
            self.inception_remote_backup_host = settings.INCEPTION_REMOTE_BACKUP_HOST
            self.inception_remote_backup_port = int(settings.INCEPTION_REMOTE_BACKUP_PORT)
            self.inception_remote_backup_user = settings.INCEPTION_REMOTE_BACKUP_USER
            self.inception_remote_backup_user = settings.INCEPTION_REMOTE_BACKUP_PASSWORD
        except:
            GetLogger().get_logger().error(traceback.format_exc())

    def _fetchall(self, sql, paramHost, paramPort, paramUser, paramPasswd, paramDb):
        '''
        封装mysql连接和获取结果集方法
        '''
        result = None
        conn = None
        cur = None
        try:
            conn=pymysql.connect(host=paramHost, user=paramUser, passwd=paramPasswd, db=paramDb, port=paramPort, charset='utf8mb4')
            cur=conn.cursor()
            ret=cur.execute(sql)
            result=cur.fetchall()
        except pymysql.Error as e:
            GetLogger().get_logger().error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
        return result

    def critical_DDL(self, sql_content):
        '''
        过滤危险的DDL语句
        DROP DATABASE, DROP TABLE, TRUNCATE PARTITION, TRUNCATE TABLE
        因为对于这些操作，inception在备份时只能备份METADATA，而不会备份数据！
        '''
        result_list = []
        critical_sql_count = 0
        for row in sql_content.rstrip(';').split(';'):
            if re.match(r"([\s\S]*)drop(\s+)database(\s+.*)|([\s\S]*)drop(\s+)table(\s+.*)|([\s\S]*)truncate(\s+)partition(\s+.*)|([\s\S]*)truncate(\s+)table(\s+.*)", row.lower()):
                result = ('', 'CHECKED', 2, '高危SQL', '不能包含 DROP DATABASE | DROP TABLE | TRUNCATE PARTITION | TRUNCATE TABLE 关键字',
                          row, '', '', 'None', '0', '')
            else:
                result = ('', 'CHECKED', 0, 'None', 'Audit completed', row, '', '', 'None', '0', '')
            result_list.append(result)
        if critical_sql_count == 1:
            return result_list
        else:
            return None

    def pre_check(self, sql_content):
        '''
        :param sql_content:
        :return:
        提交inception之前需要识别inception不能正确审核的sql，比如"alter table t1;"或"alter table test.t1;" 以免导致inception core dump
        '''
        result_list = []
        syntax_error_sql_found = 0
        for row in sql_content.rstrip(';').split(';'):
            if re.match(r"(\s*)alter(\s+)table(\s+)(\S+)(\s*);|(\s*)alter(\s+)table(\s+)(\S+)\.(\S+)(\s*);",row.lower() + ";"):
                result = ('', 'CHECKED', 2, 'SQL语法错误', 'ALTER TABLE 必须带有选项', row, '', '', 'None', '0', '')
                syntax_error_sql_found = 1
            else:
                result = ('', 'CHECKED', 0, 'None', 'Audit completed', row, '', '', 'None', '0', '')
            result_list.append(result)
        if syntax_error_sql_found == 1:
            return result_list
        else:
            return None



    #将sql 交给inception进行自动审核，并返回审核结果
    def sql_auto_review(self, sql_content, cluster_db_name, is_split=False):
        '''
        :param sql_content: sql文本
        :param db_name: localhost->test
        :param is_split:
        :return:  (
                 (ID: sql序号,
                 stage: 当前语句进行到哪一步:CHECKED、EXECUTED、RERUN、NONE，NONE,
                 errlevel: 0 正常; 1 警告; 2 严重错误,
                 stagestatus: 检查执行过程是成功还是失败,
                 errormessage: 出错错误信息，
                 SQL: 执行哪条sql,
                 affected_rows: sql执行影响的行数,
                 sequence: 回滚序列号,
                 backup_dbname: 备份库的信息,
                 execute_time: 执行时间,
                 SQLSHA1: OSC功能
                 )
                 (1,'CHECKED',0,'Audit completed','None','use django',0,"'0_0_0'",'None','0',''),
                 (2,'CHECKED',1,'Audit completed',"Identifier 'name' is keyword in MySQL.","insert into auth_group (name) values ('inception')",1,"'0_0_1'",'127_0_0_1_3306_django','0','')
                 )
        '''
        cluster_name, db_name = cluster_db_name.split('->')
        master_db = MasterConfig.objects.get(Q(cluster_name=cluster_name) and Q(db_name=db_name))
        master_host = master_db.master_host
        master_port = master_db.master_port
        master_user = master_db.master_user
        master_password = master_db.master_passwd

        if settings.CRITICAL_DDL_ON_OFF:
            check_result = self.critical_DDL(sql_content)
        else:
            check_result = None
        if check_result is not None:
            result = check_result
        else:
            pre_check_result = self.pre_check(sql_content)
            if pre_check_result is not None:
                result = pre_check_result
            else:
                if is_split:
                    # 这种场景只给osc进度功能使用
                    # 如果一个工单中同时包含DML和DDL，那么执行时被split后的SQL与提交的SQL会不一样（会在每条语句前面加use database;)，导致osc进度更新取不到正确的SHA1值。
                    # 请参考inception文档中--enable-split参数的说明
                    # --enable-execute --enable-split
                    sql_inception =  "/*--user=%s; --password=%s; --host=%s; --port=%s; --enable-check; --enable-ignore-warnings; --enable-split;*/\
                                      inception_magic_start;\
                                      %s\
                                      inception_magic_commit;" %(master_user, master_password, master_host, str(master_port), sql_content)
                    sql_result = self._fetchall(sql_inception, paramHost=self.inception_host, paramPort=self.inception_port, paramUser='', paramPasswd='', paramDb='')
                    tmp_list = []
                    if sql_result is None or len(sql_result) == 0:
                        result = (('', 'CHECKED', 2, 'SQL语法错误', '未知语法错误，inception奔溃', '', '', '', 'None', '0', ''), )
                        return result
                    for row in sql_result:
                        sql_split = row[1]
                        sql = "/*--user=%s; --password=%s; --host=%s; --port=%s; --enable-check; --enable-ignore-warnings;*/\
                                inception_magic_start;\
                                %s\
                                inception_magic_commit;" %(master_user, master_password, master_host, str(master_port), sql_split)
                        split_sql_result = self._fetchall(sql, paramHost=self.inception_host, paramPort=self.inception_port, paramUser='', paramPasswd='', paramDb='')
                        tmp_list.append(split_sql_result)

                    final_list = []
                    #去掉外层list
                    for row in tmp_list:
                        for sql_row in row:
                            final_list.append(tuple(sql_row))
                    result = tuple(final_list)
                else:
                    sql_inception =  "/*--user=%s; --password=%s; --host=%s; --port=%s; --enable-check; --enable-ignore-warnings;*/\
                                      inception_magic_start;\
                                      %s\
                                      inception_magic_commit;" % (master_user, master_password, master_host, str(master_port), sql_content)
                    result = self._fetchall(sql_inception, paramHost=self.inception_host, paramPort=self.inception_port, paramUser='', paramPasswd='', paramDb='')

        return result
