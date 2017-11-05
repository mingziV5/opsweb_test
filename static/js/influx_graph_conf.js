/**
 * Created by rongjunfeng on 2017/9/20.
 */

var  graph_option = {
    title: {
        left: "center",
        target: "self"
    },
    tooltip: {
        trigger: 'axis'
        /*
        formatter:function(params) {
            var ret = params[0].axisValueLabel + "<br>";
            $.each(params, function(i, obj){
                var value;
                if(obj.value ){
                    value = (obj.value / 1024 /1024 /1024).toFixed(2)
                }else{
                    value = "";
                }
                ret += obj.marker + " "  + obj.seriesName + ": " + value + "</br>"
            });

            return ret
        }*/
    },

    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        name: "时间",
        boundaryGap: false,
        data: []
    },
    yAxis: {
        type: 'value',
        splitLine: {
            show: true
        }
        /*
        axisLabel:{
            formatter: function(category){
                return (category / 1024 / 1024 / 1024).toFixed(1)
                //return category
            }
        }*/
    },
    series: []
};

function flush_graph(influx_api, obj,graph_id, graph_time) {
    console.log("刷新echart");
    $.ajax({
        url: influx_api,
        type: "get",
        data: {"graph_id": graph_id},
        success: function (res) {
            if (res.status != 0){
                swal("操作失败", res.errmsg, "error")
            }else{
                obj.setOption({
                    xAxis: {
                        data: res.categories
                    },
                    series: res.series
                });
            }
        }
    });
}