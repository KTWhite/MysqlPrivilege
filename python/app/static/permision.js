	$(function(){
   		　　//初始加载，表格宽度自适应
		    $(document).ready(function(){
		        fitCoulms();
		    });
		　　//浏览器窗口大小变化后，表格宽度自适应
		    $(window).resize(function(){
		        fitCoulms();
		    });
		    function fitCoulms(){
			    $('#dg').datagrid({
			        fitColumns:true
			    });
			     $('#userdg').datagrid({
			        fitColumns:true
			    });
			      $('#db').datagrid({
			        fitColumns:true
			    });
			       $('#table').datagrid({
			        fitColumns:true
			    });
			}
			//页面加载显示内容： 信源表格  加载所有信源数据
			$('#dg').datagrid({
			    url:'/sys/dbconfig',
			    method:'post',
			    title:'数据源信息表格',
			    iconCls:'icon-add,icon-edit,icon-remove',
			    fitColumns:true,
			    singleSelect:true,
			    rownumbers:true,
			    height: window.innerHeight - 45,
			    toolbar:[{
			    text:'添加',
			    iconCls:'icon-add',
			    handler:function(){
			        $.messager.alert('Warning','请先选择对象！');
			    }
			    },{
			    text:'修改',
			    iconCls:'icon-edit',
			    handler:function(){
			        $.messager.alert('Warning','请先选择对象！');
			    }
			    },{
		            text:'关联用户',
		            iconCls:'icon-add',
		            handler:function(){
		                $.messager.alert('Warning','请先选择对象！');
		            }
		            },{
			    text:'解除关联',
			    iconCls:'icon-remove',
			    handler:function(){
			        $.messager.alert('Warning','请先选择对象！');
			    }
			    },{
			    text:'删除',
			    iconCls:'icon-cancel',
			    handler:function(){
			        $.messager.alert('Warning','请先选择对象！');
			    }
			    }],
			    columns:[[
			            { field: 'check', checkbox: true },
			        	{ field: 'kid', title: '键id', width: 40,hidden:true},
			        	{ field: 'name', title: '源别名', width: 100, align: 'center' },
						{ field: 'host', title: 'ip地址', width: 100, align: 'center'  },
						{ field: 'user', title: '用户名', width: 80, align: 'center'  },
						{ field: 'password', title: '密码', width: 80, align: 'center',hidden:true  },
						{ field: 'password2', title: '密码', width: 80, align: 'center' },
						{ field: 'port', title: '端口号', width: 80, align: 'center'  },
						{ field: 'isconn', title: '关联状态', width: 80, align: 'center'  }
			    ]],
			})
			//数据库表格 加载所有数据库表格信息
	        $('#db').datagrid({
	            url:'/sys/dblists',
	            method:'post',
	            title:'数据库库列表',
	            iconCls:'icon-add,icon-edit,icon-remove',
	            fitColumns:true,
	            singleSelect:true,
	            height: window.innerHeight - 45,
	            columns:[[
	                	{ field: 'database', title: '数据库库名', width: 80, align: 'center'},
	            ]],
	    	})
	    	//数据库表的表格信息 加载所有的授权表
   	        $('#table').edatagrid({
                url:'/sys/tablelists',
                method:'post',
                title:'数据库表权限表格',
                iconCls:'icon-add,icon-edit,icon-remove',
                height: window.innerHeight - 45,
                rownumbers:true,
                singleSelect:true,
                selectOnCheck: true,
                checkOnSelect: true,
                fitColumns:true,
                toolbar:[{
                text:'授权',
                iconCls:'icon-edit',
                handler:function(){
                    $.messager.alert('Info','请选择对象！');
                }
                },{
                    text:'撤销授权',
                    iconCls:'icon-remove',
                handler:function(){
                    $.messager.alert('Info','请选择对象！');
                }
                    },{
                text:'刷新',
                iconCls:'icon-reload',
                handler:function(){
                        $('#table').edatagrid('reload')
                }
                }],
                columns:[[
                        { field: 'check', checkbox: true },
                        { field: 'id', title: 'ID', width: 20, align: 'center'},
                        { field: 'table', title: '数据库表名', width: 50, align: 'center'},
                        { field: 'all', title: 'All', width: 40, align: 'center',
                            editor:{
                                type:'checkbox',
                                options: { on: "y", off: "" }
                            }
                         },
                        { field: 'select', title: 'Select', width: 40, align: 'center',
                            editor:{
                                type:'checkbox',
                                options: { on: "y", off: "" }
                            }
                         },
                        { field: 'update', title: 'Upadte', width: 40, align: 'center',
                            editor:{
                                type:'checkbox',
                                options: { on: "y", off: "" }
                            }
                         },
                        { field: 'insert', title: 'Insert', width: 40, align: 'center',
                            editor:{
                                type:'checkbox',
                                options: { on: "y", off: "" }
                            }
                         },
                        { field: 'delete', title: 'Delete', width: 40, align: 'center',
                            editor:{
                                type:'checkbox',
                                options: { on: "y", off: "" }
                            }
                         },
                ]],
            })
			//加载所有的用户信息的表格
   	        $('#userdg').datagrid({
	            url:'/sys/userlist',
	            method:'post',
	            title:'用户列表表格',
	            iconCls:'icon-add,icon-edit,icon-remove',
	            fitColumns:true,
	            singleSelect:true,
	            height: window.innerHeight - 45,
	            columns:[[
	                    { field: 'id', title: '用户id', width: 80,hidden:true},//主键id
	                	{ field: 'user', title: '用户名', width: 125,align: 'center',hidden:true},
	                	{ field: 'password', title: '密码', width: 125,align: 'center',hidden:true},
	                	{ field: 'realname', title: '用户真名', width: 80,align: 'center'},
	                	{ field: 'email', title: '电子邮箱', width: 160,align: 'center'},
	            ]],
            onClickRow:function(index,urow){
            	$('#dg').datagrid({
		            url:'/sys/dglist',
		            method:'post',
		            title:'数据源信息表格',
		            height: window.innerHeight - 45,
		            iconCls:'icon-add,icon-edit,icon-remove',
		            queryParams:{'uid':urow.id},
		            fitColumns:true,
		            singleSelect:true,
		            rownumbers:true,
		            toolbar:[{
		            text:'添加',
		            iconCls:'icon-add',
		            handler:function(){
		                $('#addsource').dialog({
		                  title:"添加源信息",
		                  width:400,
		                  height:200,
		                  closed:false,
		                  cache:false,
		                   modal:true,
		                   onOpen:function(){
		                        $('#uid').val(urow.id)
		                   }
		                })
		            }
		            },{
		            text:'修改',
		            iconCls:'icon-edit',
		            handler:function(){
		                 var row = $('#dg').datagrid('getSelected');
		                if (row) {
		                    $('#dd').dialog({
		                        title:'修改源数据',
		                        width:400,
		                        height:200,
		                        closed:false,
		                        cache:false,
		                        modal:true,
		                        onOpen:function(){
		                            $.ajax({
		                                url:'/sys/editsourceshow?id='+row.kid,
		                                dataType:'json',
		                                success:function(data){
		                                    $('#editorid').val(data.sid)
		                                    $('#editorname').val(data.name)
		                                    $('#edithost').val(data.host)
		                                    $('#editoruser').val(data.root)
		                                    $('#editorpassword').val(data.password)
		                                    $('#editordatabase').val(data.port)
		                                }
		                            })
		                        }
		                    })
		                }else{
		                    $.messager.alert('Warning','请先选择源数据！');
		                }
		            }
		            },{
		            text:'关联用户',
		            iconCls:'icon-add',
		            handler:function(){
		                var row = $('#dg').datagrid('getSelected');
		                if(!row){
                            $.messager.alert('Warning','请先选择源数据！');
		                }else{
                            $.ajax({
                                url:'/sys/crmysqluser',
                                data:{'host':row.host,'root':row.user,'password':row.password,'port':row.port,'user':urow.user,'pwd':urow.password,'kid':row.kid},
                                type:'post',
                                dataType:'json',
                                success:function(data){
                                    if(data.code==1){
                                        $.messager.alert("信息提示","用户成功关联源数据！",'info');
                                        $('#dg').datagrid("reload");
                                    }else if(data.code == 0){
                                        $.messager.alert('信息提示','关联源数据失败，请核对用户信息或源信息！',"info");
                                        $('#dg').datagrid("reload");
                                    }else if(data.code == 2){
                                        $.messager.alert('信息提示','数据库配置信息错误或该源数据库无权限关联！',"info");
                                        $('#dg').datagrid("reload");
                                    }else if(data.code == 3){
                                        $.messager.alert('信息提示','该源已经关联无需再次关联！',"info");
                                        $('#dg').datagrid("reload");
                                    }else if(data.code == 4){
                                        $.messager.alert('系统异常','关联中源状态修改失败！',"info");
                                        $('#dg').datagrid("reload");
                                    }
                                },
                                error:function(){
                                    $.messager.alert('信息提示','无权限关联用户',"info");
                                }
                            })
		                }
		            }
		            },{
		            text:'解除关联',
		            iconCls:'icon-remove',
		            handler:function(){
		                 var row = $('#dg').datagrid('getSelected');
		                if (row) {
		                    $.messager.confirm("信息提示","确定要解除关联(删除用户)？",function(result){
		                        if(result){
		                            $.ajax({
		                                url:'/sys/delmysql',
		                                data:{'user':urow.user,'id':row.kid,'host':row.host,'root':row.user,'password':row.password,'port':row.port},
		                                success:function(data){
		                                    if(data.code==1){
		                                        $.messager.alert("信息提示","成功解除关联！",'info');
		                                        $('#dg').datagrid("reload");
		                                    }else if(data.code == 2){
		                                        $.messager.alert("信息提示","无权限删除用户或不存在该用户！",'info');
		                                        $('#dg').datagrid("reload");
		                                    }else if(data.code ==0){
		                                        $.messager.alert('信息提示','系统异常，删除失败!',"info");
		                                        $('#dg').datagrid("reload");
		                                    }else if(data.code == 3){
		                                        $.messager.alert('信息提示','错误的源配置信息',"info");
		                                        $('#dg').datagrid("reload");
		                                    }

		                                }
		                            })
		                        }
		                    })
		                }else{
		                    $.messager.alert('Warning','请先选择源数据！');
		                }
		            }
		            },{
		            text:'删除',
		            iconCls:'icon-cancel',
		            handler:function(){
		                 var row = $('#dg').datagrid('getSelected');
		                if (row) {
		                    $.messager.confirm("信息提示","确定要删除该条信息吗？",function(result){
		                        if(result){
		                            $.ajax({
		                                url:'/sys/delmysql2',
		                                data:{'id':row.kid,'uid':urow.id,'ip':row.host,'root':row.user,'password':row.password,'port':row.port,'user':urow.user},
		                                success:function(data){
		                                    if(data.code==1){
		                                        $.messager.alert("信息提示","成功删除数据源！",'info');
		                                        $('#dg').datagrid("reload");
		                                    }else if(data.code ==0){
		                                        $.messager.alert('信息提示','系统异常，删除失败!',"info");
		                                        $('#dg').datagrid("reload");
		                                    }else if(data.code ==2){
		                                        $.messager.alert('信息提示','请先解除关联！',"info");
		                                        $('#dg').datagrid("reload");
		                                    }
		                                }
		                            })
		                        }
		                    })
		                }else{
		                    $.messager.alert('Warning','请先选择源数据！');
		                }
		            }
		            }],
				    columns:[[
				            { field: 'check', checkbox: true },
				        	{ field: 'kid', title: '键id', width: 40,hidden:true},
				        	{ field: 'name', title: '源别名', width: 100, align: 'center' },
							{ field: 'host', title: 'ip地址', width: 100, align: 'center'  },
							{ field: 'user', title: '用户名', width: 80, align: 'center'  },
							{ field: 'password', title: '密码', width: 80, align: 'center',hidden:true  },
							{ field: 'password2', title: '密码', width: 80, align: 'center' },
							{ field: 'port', title: '端口号', width: 80, align: 'center'  },
							{ field: 'isconn', title: '关联状态', width: 80, align: 'center'  },

				    ]],
		            onClickRow:function(index,rows){
		            	//获取指定源的数据库信息
		            	$('#db').datagrid({
				            url:'/sys/dblist',
				            method:'post',
				            title:'数据库库列表',
				            iconCls:'icon-add,icon-edit,icon-remove',
				            fitColumns:true,
				            queryParams:{'host':rows.host,'root':rows.user,'password':rows.password,'port':rows.port},
				            singleSelect:true,
				            columns:[[
				                	{ field: 'database', title: '数据库库名', width: 80,align: 'center'},
				            ]],
					            onClickRow:function(index,drow){
					                	    	//数据库表的表格信息 加载所有的授权表
					                $('#table').edatagrid({
                                        url:'/sys/tablelist',
                                        method:'post',
                                        title:'数据库表权限表格',
                                        iconCls:'icon-add,icon-edit,icon-remove',
                                        rownumbers:true,
                                        fitColumns:true,
                                        singleSelect:true,
                                        selectOnCheck: true,
                                        checkOnSelect: true,
                                        pageList: [20,40,60,80,100,120,140,160,180],
                                        pageSize:20,
                                        pagination : true,
                                        fit:true,
                                        queryParams:{'host':rows.host,'root':rows.user,'port':rows.port,'password':rows.password,"database":drow.database,'user':urow.user},
                                        fitColumns:true,
                                        toolbar:[{
                                        text:'授权',
                                        iconCls:'icon-edit',
                                        handler:function(){
                                            $('#table').edatagrid('saveRow')
                                            var selectedrows = $('#table').edatagrid('getSelected')
                                            if(selectedrows){
                                                var row =selectedrows
                                                var list = new Array()
                                                if(row['all']=="y"){
                                                    list.push("all")
                                                }else{
                                                    if(row['select']=="y"){
                                                        list.push('select')
                                                    }
                                                    if(row['alter']=="y"){
                                                        list.push('alter')
                                                    }
                                                    if(row['delete']=="y"){
                                                        list.push('delete')
                                                    }
                                                    if(row['drop']=="y"){
                                                        list.push('drop')
                                                    }
                                                    if(row['index']=="y"){
                                                        list.push('index')
                                                    }
                                                    if(row['insert']=="y"){
                                                        list.push('insert')
                                                    }
                                                    if(row['update']=="y"){
                                                        list.push('update')
                                                    }
                                                }
                                                $.ajax({
                                                    url:'/sys/privilege',
                                                    data:{'list':list,'host':rows.host,'root':rows.user,'password':rows.password,
                                                    "database":drow.database,'table':row.table,'user':urow.user,'port':rows.port,'expire':row.expire},
                                                    dataType:'json',
                                                    type:'POST',
                                                    success:function(data){
                                                        console.log(list)
                                                        if(data.code==1){
                                                            $.messager.alert('Info','授权成功！');
                                                            $('#table').edatagrid('reload');
                                                        }else if(data.code==0){
                                                            $.messager.alert('Info','源无权限授予用户权限！');
                                                            $('#table').edatagrid('reload');
                                                        }else if(data.code ==2){
                                                            $.messager.alert('Info','源数据连接异常');
                                                            $('#table').edatagrid('reload');
                                                        }else if(data.code==3){
                                                            $.messager.alert('Info','请勾选具体权限！');
                                                            $('#table').edatagrid('reload');
                                                        }

                                                    },
                                                    error:function(data){
                                                        $.messager.alert('Warnning','授权失败！');
                                                        $('#table').edatagrid('reload')
                                                    }
                                                })
                                            }
                                            else{
                                                $.messager.alert("Warnning","请选择对象！",'info');
                                            }
                                        }
                                        },{
                                            text:'撤销授权',
                                            iconCls:'icon-remove',
                                        handler:function(){
                                            $('#table').edatagrid('saveRow')
                                            var selectedrows = $('#table').edatagrid('getSelected')
                                            if(selectedrows){
                                                var row =selectedrows
                                                var list = new Array()
                                                if(row['all']=="y"){
                                                    list.push("all")
                                                }else{
                                                    if(row['select']=="y"){
                                                        list.push('select')
                                                    }
                                                    if(row['alter']=="y"){
                                                        list.push('alter')
                                                    }
                                                    if(row['delete']=="y"){
                                                        list.push('delete')
                                                    }
                                                    if(row['drop']=="y"){
                                                        list.push('drop')
                                                    }
                                                    if(row['index']=="y"){
                                                        list.push('index')
                                                    }
                                                    if(row['insert']=="y"){
                                                        list.push('insert')
                                                    }
                                                    if(row['update']=="y"){
                                                        list.push('update')
                                                    }
                                                }
                                                $.ajax({
                                                    url:'/sys/unprivilege',
                                                    data:{'list':list,'host':rows.host,'root':rows.user,'password':rows.password,
                                                    "database":drow.database,'table':row.table,'port':rows.port,'user':urow.user},
                                                    dataType:'json',
                                                    type:'POST',
                                                    success:function(data){
                                                        console.log(list)
                                                        if(data.code==1){
                                                            $.messager.alert('Info','撤销授权成功！');
                                                            $('#table').edatagrid('reload')
                                                        }else if(data.code==0){
                                                            $.messager.alert('Info','源无权限撤销用户权限');
                                                            $('#table').edatagrid('reload')
                                                        }

                                                    },
                                                    error:function(data){
                                                        $.messager.alert('Warnning','撤销授权失败！');
                                                        $('#table').edatagrid('reload')
                                                    }
                                                })
                                            }
                                            else{
                                                $.messager.alert("Warnning","请选择对象！",'info');
                                            }
                                        }
                                            },{
                                        text:'刷新',
                                        iconCls:'icon-reload',
                                        handler:function(){
                                                $('#table').edatagrid('reload')
                                        }
                                        },{
                                        text:'请双击行,进入编辑模式！',

                                        }],
                                        columns:[[
                                                { field: 'check', checkbox: true },
//                                                { field: 'id', title: 'ID', width: 20, align: 'center'},
                                                { field: 'table', title: '数据库表名', width: 50, align: 'center'},
                                                { field: 'all', title: 'All', width: 40, align: 'center',
                                                    editor:{
                                                        type:'checkbox',
                                                        options: { on: "y", off: "" }
                                                    }
                                                 },
                                                { field: 'select', title: 'Select', width: 40, align: 'center',
                                                    editor:{
                                                        type:'checkbox',
                                                        options: { on: "y", off: "" }
                                                    }
                                                 },
                                                { field: 'update', title: 'Upadte', width: 40, align: 'center',
                                                    editor:{
                                                        type:'checkbox',
                                                        options: { on: "y", off: "" }
                                                    }
                                                 },
                                                { field: 'insert', title: 'Insert', width: 40, align: 'center',
                                                    editor:{
                                                        type:'checkbox',
                                                        options: { on: "y", off: "" }
                                                    }
                                                 },
                                                { field: 'delete', title: 'Delete', width: 40, align: 'center',
                                                    editor:{
                                                        type:'checkbox',
                                                        options: { on: "y", off: "" }
                                                    }
                                                 },
                                        ]],
                                    })
					            }
		            	})
		            }
		        })

            }
    	})
	$('#dbadd').click(function(){
		    $.ajax({
			    url:'#',
			    dataType:'json',
			    data:$("#dbform").serialize(),
			    success:function(data){
			       $.messager.alert('Info','数据库添加成功！');
		    }
		})
	})
	$('#sadd').click(function(){
	        if($('#addname').val()==""){
	            $.messager.alert('Info','请输入源别名！');
	        }else if($('#addhost').val()==""){
	            $.messager.alert('Info','请输入ip地址');
	        }else if($('#adduser').val()==""){
	            $.messager.alert('Info','请输入用户名');
	        }else if($('#addpassword').val()==""){
	            $.messager.alert('Info','请输入密码');
	        }else if($('#adddatabase').val()==""){
	            $.messager.alert('Info','请输入端口号');
	        }else{
                $.ajax({
                    url:'/sys/addmysql',
                    dataType:'json',
                    data:$("#addform").serialize(),
                    type:"POST",
                    success:function(data){
                       if(data.code==1){
                            $.messager.alert('Info','信源配置添加成功！');
                            $("#addsource").dialog('close')
                            $('#dg').datagrid("reload");
                       }
                       if(data.code ==2){
                            $.messager.alert('Warnning','信源配置添加失败！');
                            $("#addsource").dialog('close')
                            $('#dg').datagrid("reload");
                       }
                       if(data.code ==3){
                            $.messager.alert('Warnning','该信源配置已经存在！无需配置');
                            $("#addsource").dialog('close')
                            $('#dg').datagrid("reload");
                       }

                    }
                })
	        }

	})
	$('#editors').click(function(){
		    $.ajax({
			    url:'/sys/editormysql',
			    dataType:'json',
			    data:$("#editorform").serialize(),
			    type:"POST",
			    success:function(data){
			       if(data.code==1){
			            $.messager.alert('Info','修改信源成功！！');
			            $("#dd").dialog('close')
			            $('#dg').datagrid("reload");
			       }else{
			            $.messager.alert('Warnning','修改信息失败！！');
			            $("#dd").dialog('close')
			            $('#dg').datagrid("reload");
			       }
		    }
		})
	})

    $('#concel2').click(function(){
        $('#dd').dialog('close')
    })
    $('#sconcel').click(function(){
        $('#addsource').dialog('close')
    })

   })