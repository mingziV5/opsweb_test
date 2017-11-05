from influxdb import InfluxDBClient
import time

class influxdbCli():
    def __init__(self):
        self.client = InfluxDBClient("192.168.1.201", database="collectd")
        #x轴数据
        self.categories = []
        #图形数据点
        self.series = []
        self.measurements = self.get_measurements()

        self.hostname = []
        self.graph_obj = None
        self.graph_time = '30m'

    def get_measurements(self):
        measurements = self.client.query("show measurements").get_points()
        return [m['name'] for m in measurements]

    def process_time(self, categories):
        ret = []
        format_str = "%Y-%m-%d %H:%M:%S"
        for point in categories:
            ret.append(time.strftime(format_str, time.localtime(point)))
        return ret

    def get_series(self, measurement, field_expression):
        if field_expression:
            field_expression = 'where ' + field_expression
        sql = "show series from {} {}".format(measurement, field_expression)
        print(sql)
        series = self.client.query(sql).get_points()
        #influxdb _key or key why??
        return [s['key'] for s in series]

    def execute(self, sql, **kwargs):
        return self.client.query(sql, **kwargs)

    '''
    例子
    def query(self):
        hostnames = ["ubuntu-xenial", "localhost"]
        sql = ""
        for hostname in hostnames:
            sql += """select mean(value) as value \
                from interface_tx \
                where time > now() - 10m \
                and type = 'if_octets' \
                and host = '{}' \
                group by time(10s) order by time desc;""".format(hostname)
        result = self.client.query(sql, epoch='s')
        #判断hostnames长度
        if len(hostnames) > 1:
            for index, hostname in enumerate(hostnames):
                self.process_data(hostname, result[index].get_points())
        else:
            self.process_data(hostnames[0], result.get_points())
    '''

    def query(self):
        where = ""
        if self.graph_obj.field_expression:
            where += " and " + self.graph_obj.field_expression
        sql = ""
        for hostname in self.hostnames:
            sql += """select mean(value) as value \
                from {} \
                where time > now() - {} \
                {} \
                and host = '{}' \
                group by time(10s) order by time desc;""".format(self.graph_obj.measurement, self.graph_time, where, hostname)

        result = self.client.query(sql, epoch="s")

        if len(self.hostnames) == 1:
            self.process_data(self.hostnames[0], result.get_points())
            return True

        for index, hostname in enumerate(self.hostnames):
            self.process_data(hostname, result[index].get_points())


    def process_data(self, hostname, data_points):
        serie = {}
        serie['name'] = hostname
        serie['type'] = 'line'
        serie['data'] = []
        categories = []
        for point in data_points:
            serie['data'].insert(0, point['value'])
            categories.insert(0, point['time'])
        self.series.append(serie)
        if not self.categories:
            self.categories = self.process_time(categories)