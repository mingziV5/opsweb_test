{% extends "public/layout.html" %}

{% block body %}
    <table class="table table-striped">
        <caption>
            <button type="button", class="btn btn-default" id="add_group">创建用户组</button>
        </caption>
        <tr>
            <th>#</th>
            <th>组名</th>
            <th>操作</th>
        </tr>
        {% for group_obj in object_list %}
            <tr>
                <td>{{ forloop.counter }}</td>
                <td>{{ group_obj.name }}</td>
                <td>
                    <a type="button" class="btn btn-primary btn-sm" href="" >成员列表</a>
                    <button type="button" class="btn btn-success btn-sm" >查看权限</button>
                    <a  class="btn btn-info btn-sm" href="#">修改权限</a>
                    <button type="button" class="btn btn-danger btn-sm del_group" groupid="{{ group.id }}">删除</button>
                </td>
            </tr>
        {% endfor %}
    </table>


<div class="modal fade" id="create_group" aria-hidden="true">
	<div class="modal-dialog">
	    <div class="modal-content">

            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal">×</button>
                <h4>添加group</h4>
            </div>
            <div class="modal-body form-inline">
                <div class="form-group">
                    <label for="exampleInputName2">用户组：</label>
                    <input type="text" class="form-control" id="form_groupname" placeholder="请输入用户组名称" />
                </div>
                <button class="btn btn-primary" id="create_group_btn">提交</button>
            </div>
            <div class="modal-footer">
                <input class="btn btn-default" data-dismiss="modal" aria-hidden="true" type="button" value="取消">
            </div>

        </div>
    </div>
</div>
{% endblock %}

{% block js %}
    <script>
        $(function () {
            //创建用户组
            $("#add_group").click(function(){
                var create_group_modal = $("#create_group");
                create_group_modal.modal("show");

                $("#create_group_btn").click(function(){
                    var group_name = $("#form_groupname").val()
                    console.log(group_name)

                    if (group_name == ""){
                        swal("添加失败", "用户组名不能为空", "error");
                        return false
                    }
                    create_group_modal.modal("hide");
                    $.ajax({
                    url: "{% url 'group_create' %}",
                    type: "post",
                    data: {"name": group_name},
                    success: function (res) {
                        if (res.status == 0){
                            swal({
                                "title": "用户组添加成功",
                                "text": "",
                                "type": "success"
                            }, function(){
                                setTimeout(function(){
                                    window.location.reload();
                                },100)

                            });
                        }else{
                            swal("操作失败", res.errmsg, "error");
                        }

                    },
                    beforeSend: function (xhr, settings) {
                        var csrftoken = getCookie('csrftoken');
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken)
                        }
                    }
                })
                })
            })
        })

    </script>
{% endblock %}