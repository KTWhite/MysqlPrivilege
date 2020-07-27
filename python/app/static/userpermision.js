	$(function(){
   		　　//初始加载，表格宽度自适应
		    $(document).ready(function(){
		        fitCoulms();
		    });
		　　//浏览器窗口大小变化后，表格宽度自适应
		    $(window).resize(function(){
		        fitCoulms();
		    });
            $('#orderdialogclose').click(function(){
                $('#applyorder').dialog('close')
            })
            $('#orderapply').click(function(){
                $.ajax({
                    url:'/index/orderapply',
                    dataType:'json',
                    data:$("#orderform").serialize(),
                    type:"POST",
                    success:function(data){
                       if(data.code==1){
                            $.messager.alert('Info','指令申请提交成功！');
                            $("#applyorder").dialog('close')
                       }else if(data.code==3){
                            $.messager.alert('Warnning','缺少；号，末尾记得加分号！');
                            $("#applyorder").dialog('close')
                       }
                    }
                })
            })
		    function fitCoulms(){
			    $('#dg').datagrid({
			        fitColumns:true
			    });
			      $('#db').datagrid({
			        fitColumns:true
			    });
			       $('#table').datagrid({
			        fitColumns:true
			    });
			}
			//数据库表格 加载所有数据库表格信息
	        $('#db').datagrid({
	            url:'#',
	            method:'post',
	            title:'数据库库列表',
	            iconCls:'icon-add,icon-edit,icon-remove',
	            fitColumns:true,
	            singleSelect:true,
	            columns:[[
	                	{ field: 'database', title: '数据库库名', width: 80,align: 'center'},
	            ]],
	    	})
	    	//数据库表的表格信息 加载所有的授权表
   	        $('#table').edatagrid({
	            url:'#',
	            method:'post',
	            title:'数据库表权限表格',
	            iconCls:'icon-add,icon-edit,icon-remove',
	            fitColumns:true,
	            singleSelect:true,
	            toolbar:[{
	            text:'申请授权',
	            iconCls:'icon-ok',
	            handler:function(){
		            	$.messager.alert('Warning','请先选择数据源配置！');
	            }
	            },
	            { text: '指令申请', iconCls: 'icon-add',
                    handler: function () {
                        $.messager.alert('Warning','请先选择数据源配置！');
                    }
                 },
                { text: '刷新', iconCls: 'icon-reload', handler: function () {
	                    var row = $('#table').datagrid("getSelected")
                        if (row) {
                            $("#table").datagrid("reload")
                        }
                        else{
                            $.messager.alert('Warning','请先选择数据源配置！');
                        }
	                }
	             }],
                columns:[[
                        { field: 'check', checkbox: true },
                        { field: 'id', title: 'ID', width: 20, align: 'center'},
                        { field: 'table', title: '数据库表名', width: 100, align: 'center'},
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
                        { field: 'expire', title: '有效天数', width: 40 , align: 'center',
                            editor:{
                                type:'numberbox',
                                options:{
                                    min:0,
                                    precision:3,
                                    values:0
                                }

                            }
                        },
                ]],
	    	})
			//页面加载显示内容： 信源表格  加载所有信源数据
			$('#dg').datagrid({
			    url:'/index/dbconfig',
			    method:'post',
			    title:'数据源信息表格',
			    iconCls:'icon-add,icon-edit,icon-remove',
			    fitColumns:true,
			    singleSelect:true,
			    rownumbers:true,
			    columns:[[
			        	{ field: 'kid', title: '键id', width: 40,hidden:true},
			        	{ field: 'name', title: '别名', width: 100, align: 'center' },
						{ field: 'host', title: 'ip地址', width: 100, align: 'center'  },
						{ field: 'user', title: '用户名', width: 80, align: 'center'  },
						{ field: 'password', title: '密码', width: 80, align: 'center',hidden:true  },
						{ field: 'password2', title: '密码', width: 80, align: 'center' },
						{ field: 'port', title: '端口号', width: 80, align: 'center'  },
						{ field: 'isconn', title: '关联状态', width: 80, align: 'center'  }
			    ]],
			    onClickRow:function(index,dcrow){
                    //数据库表格 加载所有数据库表格信息
                    $('#db').datagrid({
                        url:'/index/dblist',
                        method:'post',
                        title:'数据库库列表',
                        iconCls:'icon-add,icon-edit,icon-remove',
                        fitColumns:true,
                        queryParams:{'host':dcrow.host,'root':dcrow.user,'password':dcrow.password,'port':dcrow.port},
                        singleSelect:true,
                        columns:[[
                                { field: 'database', title: '数据库库名', width: 80,align: 'center'},
                        ]],
                        onClickRow:function(index,dbrow){
                            $('#table').edatagrid({
                                        url:'/index/tablelist',
                                        method:'post',
                                        title:'数据库表权限表格',
                                        iconCls:'icon-add,icon-edit,icon-remove',
                                        queryParams:{'host':dcrow.host,'root':dcrow.user,'password':dcrow.password,'port':dcrow.port,"database":dbrow.database},
                                        fitColumns:true,
                                        singleSelect:true,
                                        pageList: [20,40,60,80,100,120,140,160,180],
                                        pageSize:20,
                                        pagination : true,
                                        fit:true,
                                        toolbar:[{
                                        text:'申请授权',
                                        iconCls:'icon-ok',
                                        handler:function(table_index){
                                            $('#table').edatagrid('saveRow')
                                            var selectedrows = $('#table').edatagrid('getSelected')
//                                            console.log(selectedrows)
                                            if (!selectedrows){
                                                $.messager.alert("信息提示","请选择表",'info');
                                            }else{
                                                //启动getEditos时要优先调用 beginEdit,row.id-1 对应的是当前行所对应的序列号 id
                                                var row =selectedrows//获取当前选中行中对应的所有列的数据
                                                var list = new Array()
                                                //ed[0]表示 选中行的第一个列信息机 第n行1列的单元格
                                                //ed[0].target 获取选中行对应单元格中editor自定义的控件 checkbox
                                                //ed[0].target.is(':checked') 判断checkbox控件是否选中
                                                // console.log(ed)
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
                                                 console.log(list)
                                                 if (list.length==0){
                                                    $.messager.alert("信息提示","请选择需要申请的权限！",'info');
                                                 }else{
                                                 //alert(list)
                                                //该ajax是对接授权接口方法
                                                    $.ajax({
                                                        url:'/index/applyfor',
                                                        data:{'list':list,"host":dcrow.host,'alias':dcrow.name,'database':dbrow.database,'table':row.table,'expire':row.expire},
                                                        dataType:'json',
                                                        type:'POST',
                                                        success:function(data){
                                                            if(data.code==1){
                                                                $.messager.alert("信息提示","权限申请等待审核...！",'info');
    //                                                            alert(list)
                                                            }
                                                            if(data.code == 2){
                                                                $.messager.alert("信息提示","系统异常...",'info');
                                                            }
        //                                                    $('#table').datagrid('reload')
                                                            if(data.code == 4){
                                                                $.messager.alert("信息提示","权限授予失败...！",'info');
                                                            }
                                                        },
                                                        error:function(data){
                                                            $.messager.alert("信息提示","权限申请失败...",'info');
        //                                                    $('#table').datagrid('reload')
                                                        }
                                                    })
                                                 }
                                            }

                                        }
                                        },{ text: '指令申请', iconCls: 'icon-add',
                                            handler: function () {
                                                $('#applyorder').dialog({
                                                  title:"申请sql指令",
                                                  width:400,
                                                  height:200,
                                                  closed:false,
                                                  cache:false,
                                                   modal:true,
                                                   onOpen:function(){
                                                        $('#targethost').val(dcrow.host)
                                                        $('#targetDb').val(dbrow.database)
                                                        $('#targetuser').val(dcrow.user)
                                                        $('#targetpwd').val(dcrow.password)
                                                        $('#targetDbName').val(dcrow.name)
                                                        $('#targetport').val(dcrow.port)
                                                   }
                                                })
                                            }
                                        },
                                        { text: '刷新', iconCls: 'icon-reload', handler: function () { $('#table').datagrid("reload") } }],
                                        columns:[[
                                                { field: 'check', checkbox: true },
                                                { field: 'id', title: 'ID', width: 20, align: 'center'},
                                                { field: 'table', title: '数据库表名', width: 100, align: 'center'},
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
                                                { field: 'expire', title: '有效天数', width: 40 , align: 'center',
                                                    editor:{
                                                        type:'numberbox',
                                                        options:{
                                                            min:0,
                                                            precision:3,
                                                            values:0
                                                        }

                                                    }
                                                },
                                        ]],
                                    })
                        }
                    })
			    }
			})
   })