# -*- encoding:utf-8 -*-
"""
@Time   :   2020/6/24 10:36 
@Author :   yanyu
@Email  :   973900834@qq.com
@Project:   
@Description    :   
"""
from flask import render_template,sessions,redirect,url_for,flash,request,jsonify,session
from . import system
import pymysql
import hashlib
from ..AES import aesEncrypt,aesDecrypt
import datetime
from python.config import Config
from apscheduler.schedulers.background import BackgroundScheduler
import time
@system.route("/index")
def index():
    root = session.get('root')
    if root is None:
        return redirect('login')
    else:
        return render_template('/system/index.html',root=root)

@system.route("/userapply")
def userapply():
    return render_template("/system/userapplyrecord.html")
@system.route("/recordlist",methods=["GET","POST"])
def recordlist():
    page = int(request.values.get('page'))
    rows = int(request.values.get('rows'))
    start = (page - 1) * rows
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from applymsg order by dbstatus asc,id desc limit {},{}".format(start,rows)
    # print(sql)
    sql2 = "select count(*) from applymsg"
    reslist = []
    try:
        try:
            cursor.execute(sql2)
            counts = cursor.fetchone()
            total = counts[0]
        except Exception as e:
            print(e)
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results) > 0:
            status = ""
            i = 1
            for result in results:
                if result[4] == 0:
                    status = "待审核"
                elif result[4] == 1:
                    status = "通过"
                elif result[4] == 2:
                    status = "拒绝"
                res = {}
                res['id'] = i
                i = i + 1
                res['rid'] = result[0]
                res['uname'] = result[2]
                res['dbalias'] = result[7]
                res['host'] = result[8]
                res['database'] = result[3]
                res['table'] = result[9]
                if result[10]=="all":
                    res['privilege'] ="select,alter,delete,drop,index,insert,update"
                else:
                    res['privilege'] = result[10]
                res['createtime'] = result[5]
                res['status'] = status
                res['expire'] = result[11]
                reslist.append(res)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "rows":reslist,
        "total":total
    })
def expireprivilege(db,table,host,privilege,users,root,decryptpwd,port):
    if host !="localhost" and host!="127.0.0.1":
        vhost = "%"
    elif host =="localhost":
        vhost ="localhost"
    elif host =="127.0.0.1":
        vhost = "127.0.0.1"
    sql = "Revoke {} on {}.{} from '{}'@'{}'".format(privilege, db, table, users, vhost)
    print(sql)
    connection = pymysql.Connection(host=host, user=root, password=decryptpwd, port=int(port), database=db)
    cursor2 = connection.cursor()
    try:
        cursor2.execute(sql)
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        cursor2.close()
        connection.close()

@system.route("/applyok",methods=["GET","POST"])
def applyok():
    recordid = request.values.get("recordid")
    db = request.values.get("db")
    table = request.values.get('table')
    host = request.values.get('ip')
    vhost = "localhost"
    privilege = request.values.get('privilege')
    users = request.values.get('user')
    dieline = request.values.get('expire')
    msg= ""
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select root,password,port from dbconfig where host = '{}' ".format(host)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        root = result[0]
        password = result[1]
        key = Config.AESKEY
        # print(Config.AESKEY)
        decryptpwd = aesDecrypt(key,password)
        port = result[2]
        cursor.close()
        conn.close()
        if dieline !="":
            if host !="localhost" and host !="127.0.0.1":
                vhost="%"
            elif host =="127.0.0.1":
                vhost ="127.0.0.1"
            privsql ="Grant {} ON {}.{} To '{}'@'{}'".format(privilege, db, table, users,vhost)
            print(privsql)
            try:
                connection = pymysql.Connection(host=host, user=root, password=decryptpwd, port=int(port), database=db)
                cursor2 = connection.cursor()
                try:
                    cursor2.execute(privsql)
                    connection.commit()
                    conn2 = get_conn()
                    cursor3 = conn2.cursor()
                    sql3 = "update applymsg set dbstatus={} where id = {}".format(1, recordid)
                    # print(sql3)
                    try:
                        cursor3.execute(sql3)
                        conn2.commit()
                        code = 1
                    except Exception as e:
                        print(e)
                        code = 0
                        msg = str(e)
                        conn2.rollback()
                    finally:
                        cursor3.close()
                        conn2.close()
                except Exception as e:
                    print(e)
                    msg = str(e)
                    code = 4
            except Exception as e:
                print(e)
                code = 2
                msg=str(e)
            t = datetime.datetime.strptime(dieline, "%Y-%m-%d %H:%M:%S")
            # print(datetime.datetime.strftime(t,"%Y-%m-%d %H:%M:%S"))
            scheduler = BackgroundScheduler()
            print("添加定时任务！")
            scheduler.add_job(func=expireprivilege, args=(db,table,host,privilege,users,root,decryptpwd,port), next_run_time=t)
            # scheduler.add_job(func=expireprivilege, args=(db, table, host, privilege, users, root, decryptpwd, port),next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=60))
            code = 1
            print("启动定时任务！")
            scheduler.start()
        else:
            if host !="localhost" and host !="127.0.0.1":
                vhost="%"
            elif host == "127.0.0.1":
                vhost ="127.0.0.1"
            sql2 = "Grant {} ON {}.{} To '{}'@'{}'".format(privilege, db, table, users,vhost)
            try:
                connection = pymysql.Connection(host=host, user=root, password=decryptpwd, port=int(port), database=db)
                cursor2 = connection.cursor()
                try:
                    cursor2.execute(sql2)
                    connection.commit()
                    conn2 = get_conn()
                    cursor3 = conn2.cursor()
                    sql3 = "update applymsg set dbstatus={} where id = {}".format(1, recordid)
                    # print(sql3)
                    try:
                        cursor3.execute(sql3)
                        conn2.commit()
                        code = 1
                    except Exception as e:
                        print(e)
                        code = 0
                        msg = str(e)
                        conn2.rollback()
                except Exception as e:
                    print(e)
                    code = 4
                    msg = str(e)
                    connection.rollback()
                finally:
                    cursor2.close()
                    connection.close()
            except Exception as e:
                print(e)
                code = 2
                msg=str(e)
    except Exception as e:
        print(e)
        code = 0
        msg = str(e)
    return jsonify({
        "code":code,
        "msg":msg
    })
@system.route("/applyno",methods=["GET","POST"])
def applyno():
    recordid = request.values.get("recordid")
    conn = get_conn()
    cursor = conn.cursor()
    now_date = datetime.datetime.now()
    nowdate = datetime.datetime.strftime(now_date, '%Y-%m-%d')
    sql = "update applymsg set dbstatus = 2,updatetime = '{}' where id = {}".format(nowdate,recordid)
    code = 0
    msg = ""
    try:
        cursor.execute(sql)
        conn.commit()
        code = 1
    except Exception as e:
        print(e)
        conn.rollback()
        msg = str(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "code":code,
        "msg":msg
    })
@system.route("/dbconfig",methods=["GET","POST"])
def dbconfig():
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from dbconfig"
    reslist = []
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results)!=0:
            for result in results:
                res = {}
                res['kid'] = result[0]
                res['name'] = result[1]
                res['host'] = result[2]
                res['user'] = result[3]
                res['password'] = result[4]
                res['password2'] = "******"
                res['port'] = result[5]
                if result[6] ==1:
                    res['isconn'] = '已关联'
                elif result[6] ==0:
                    res['isconn'] = "未关联"
                reslist.append(res)
    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "rows":reslist
    })
@system.route("/dblists",methods=["GET","POST"])
def dblists():
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from dbconfig"
    reslist = []
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        key = Config.AESKEY
        if len(results)>0:
            for result in results:
                decryptpwd = aesDecrypt(key,result[4])
                try:
                    connection = pymysql.Connection(host=result[2], user=result[3], password=decryptpwd, port=int(result[5]))
                    sql2 = "show databases"
                    cursor2 = connection.cursor()
                    try:
                        cursor2.execute(sql2)
                        datas = cursor2.fetchall()
                        for data in datas:
                            res = {}
                            if data[0] != "information_schema" and data[0] != "mysql" and data[0] != "sys" and data[
                                0] != "performance_schema":
                                res['database'] = data[0]
                                reslist.append(res)
                    except Exception as e:
                        print(e)
                    finally:
                        cursor2.close()
                        connection.close()
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "rows":reslist
    })
@system.route("/tablelists",methods=["GET","POST"])
def tblist():
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from dbconfig"
    reslists = []
    key = Config.AESKEY
    try:
        cursor.execute(sql)
        dbconfiglist = cursor.fetchall()
        if len(dbconfiglist) > 0:
            for dbconfig in dbconfiglist:
                connection = pymysql.Connection(host=dbconfig[2], user=dbconfig[3], password=aesDecrypt(key,dbconfig[4]),
                                                port=int(dbconfig[5]), database='information_schema')
                if connection is not None:
                    cursor2 = connection.cursor()
                    sql2 = "select a.TABLE_NAME as 'table',GROUP_CONCAT(a.PRIVILEGE_TYPE order by a.PRIVILEGE_TYPE SEPARATOR ',' ) as 'privilege' from TABLE_PRIVILEGES as a group by a.TABLE_NAME "
                    try:
                        sqlres = cursor2.execute(sql2)
                        if sqlres is not None:
                            tablelists = cursor2.fetchall()
                            # print(tablelists)
                            if len(tablelists) > 0:
                                i = 1
                                for result in tablelists:
                                    if result[0] != "sys_config":
                                        res = {}
                                        res['id'] = i
                                        i = i + 1
                                        res['all'] = ""
                                        res['select'] = ""
                                        res['update'] = ""
                                        res['insert'] = ""
                                        res['delete'] = ""
                                        res['drop'] = ""
                                        res['index'] = ""
                                        res['alter'] = ""
                                        res['table'] = result[0]
                                        privlist = result[1].split(',')
                                        for priv in privlist:
                                            key = priv.lower()
                                            if key in res.keys():
                                                res[key] = "y"
                                        reslists.append(res)
                    except Exception as e:
                        print(e)
                    finally:
                        cursor2.close()
                        connection.close()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "rows": reslists
    })
@system.route("/deldata")
def deldata():
    id = request.values.get('id')
    sql=""
    sql2 = ""
    if id=="":
        code=400
    else:
        sql = "delete from user where uid = {}".format(int(id))
        sql2 = "delete from dbconfig where uid = {}".format(int(id))
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        cursor.execute(sql2)
        conn.commit()
        code=200
    except Exception as e:
        print(e)
        code=400
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return jsonify(
        {'code':code}
    )
@system.route("/permision2",methods=["GET","POST"])
def permision2():
    return render_template("/system/permision.html")
@system.route("/privilege",methods=["GET","POST"])
def privilege():
    user = request.values.get('user')
    # print(user)
    lists = request.values.getlist('list[]')
    if len(lists)==0:
        return jsonify({
            "code": 3,
            "msg": ""
        })
    else:
        # print(lists)
        database = request.values.get('database')
        # print(database)
        table = request.values.get('table')
        # print(table)
        host = request.values.get('host')
        vhost = "localhost"
        # print(host)
        root = request.values.get('root')
        # print(root)
        password = request.values.get('password')
        # print(password)
        # expire = request.values.get('expire')
        # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        key = Config.AESKEY
        decryptpwd = aesDecrypt(key,password)
        port = request.values.get('port')
        msg = ""
        try:
            conn = pymysql.Connection(host=host, user=root, password=decryptpwd, database=database, port=int(port))
            cursor = conn.cursor()
            code = 0
            if host != "localhost" and host !="127.0.0.1":
                vhost = "%"
            elif host =="127.0.0.1":
                vhost = "127.0.0.1"
            if lists[0] != "all":
                string = ",".join(lists)
                # print(string)
                sql = "Grant {} ON {}.{} To '{}'@'{}'".format(string, database, table, user,vhost)
            else:
                sql = "Grant  select,alter,delete,drop,index,insert,update ON {}.{} To '{}'@'{}'".format(database, table, user,vhost)
            try:
                cursor.execute(sql)
                conn.commit()
                code = 1
            except Exception as e:
                print(e)
                msg = str(e)
                code = 0
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(e)
            code = 2
            msg = str(e)
        return jsonify({
            "code":code,
            "msg":msg
        })
@system.route("/unprivilege",methods=["GET","POST"])
def unprivilege():
    user = request.values.get('user')
    # print(user)
    lists = request.values.getlist('list[]')
    # print(lists)
    database = request.values.get('database')
    # print(database)
    table = request.values.get('table')
    # print(table)
    host = request.values.get('host')
    vhost = "localhost"
    # print(host)
    root = request.values.get('root')
    # print(root)
    password = request.values.get('password')
    # print(password)
    key = Config.AESKEY
    decryptpwd = aesDecrypt(key,password)
    port = request.values.get('port')
    msg = ""
    try:
        conn = pymysql.Connection(host=host, user=root, password=decryptpwd, database=database, port=int(port))
        cursor = conn.cursor()
        if host !="localhost" and host !="127.0.0.1":
            vhost = "%"
        elif host == "127.0.0.1":
            vhost = "127.0.0.1"
        if lists[0]!="all":
            string = ",".join(lists)
            sql = "Revoke {} on {}.{} from '{}'@'{}'".format(string, database, table, user,vhost)
        else:
            sql = "Revoke select,alter,delete,drop,index,insert,update on {}.{} from '{}'@'{}'".format(database, table, user,vhost)
        # print(string)
        code = 0
        try:
            print(sql)
            cursor.execute(sql)
            conn.commit()
            code = 1
        except Exception as e:
            print(e)
            code = 0
            msg = str(e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(e)
        code = 2
        msg = str(e)
    return jsonify({
        "code":code,
        "msg":msg
    })
#-------------------------表格动态数据展示----------------------
@system.route("/userlist",methods=["GET","POST"])
def userlist():
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select uid,name,realname,email,password from user "
    reslist = []
    try:
        cursor.execute(sql)
        results = cursor.fetchall()

        for result in results:
            res={}
            res['id'] = result[0]
            res['user'] = result[1]
            res['realname'] = result[2]
            res['email'] = result[3]
            res['password'] = result[4]
            reslist.append(res)
    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        'rows':reslist
    })
@system.route("/dglist",methods=["GET","POST"])
def dglist():
    uid = request.values.get('uid')
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from dbconfig where uid={}".format(uid)
    reslist = []
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            res = {}
            if result[6] == 0:
                res['isconn'] = "未关联"
            elif result[6] ==1:
                res['isconn'] = "已关联"
            res['kid'] = result[0]
            res['name'] = result[1]
            res['host'] = result[2]
            res['user'] = result[3]
            res['password'] = result[4]
            res['password2'] = "******"
            res['port'] = result[5]
            reslist.append(res)
    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "rows":reslist
    })
@system.route("/dblist",methods=["GET","POST"])
def dblist():
    host = request.values.get("host")
    root = request.values.get('root')
    password = request.values.get('password')
    key = Config.AESKEY
    decryptpwd = aesDecrypt(key,password)
    port = request.values.get('port')
    db = "mysql"
    reslist = []
    try:
        conn = pymysql.Connection(host=host, user=root, password=decryptpwd, port=int(port))
        cursor = conn.cursor()
        sql = "show DATABASES"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for result in results:
                # print(result[0])
                res = {}
                if result[0]!="information_schema" and result[0]!="mysql" and result[0]!="sys" and result[0]!="performance_schema":
                    res['database'] = result[0]
                    reslist.append(res)
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(e)
    return jsonify({
        "rows":reslist
    })
@system.route("/tablelist",methods=["GET","POST"])
def tablelist():
    page = int(request.values.get("page"))
    rows = int(request.values.get('rows'))
    start = (page - 1) * rows
    user = request.values.get('user')
    host = request.values.get('host')
    vhost = "localhost"
    root = request.values.get('root')
    password = request.values.get('password')
    key = Config.AESKEY
    decryptpwd = aesDecrypt(key, password)
    port = request.values.get('port')
    database = request.values.get('database')
    reslists = []
    tablelist=[]
    conn = pymysql.Connection(host=host, user=root, password=decryptpwd,
                              port=int(port), database=database)
    tablecursor = conn.cursor()
    tsql = "show tables"
    try:
        tablecursor.execute(tsql)
    except Exception as e:
        print(e)
    tables = tablecursor.fetchall()
    for table in tables:
        tablelist.append(table[0])
    connection = pymysql.Connection(host=host, user=root, password=decryptpwd,
                                    port=int(port), database='information_schema')
    cursor = connection.cursor()
    if host !="localhost" and host !="127.0.0.1":
        vhost = "%"
    elif host =="127.0.0.1":
        vhost = "127.0.0.1"
    grantee = "'{}'@'{}'".format(user,vhost)
    # print(grantee)
    sql2 = "select a.TABLE_NAME as 'table',GROUP_CONCAT(a.PRIVILEGE_TYPE order by a.PRIVILEGE_TYPE SEPARATOR ',' ) as 'privilege' from TABLE_PRIVILEGES as a where  TABLE_SCHEMA ='{}' and GRANTEE =\"{}\" group by a.TABLE_NAME ".format(database,grantee)
    print(sql2)
    try:
        cursor.execute(sql2)
        tablelists = cursor.fetchall()
        # print(tablelists)
        if len(tablelists) > 0:
            i = 1
            for result in tablelists:
                if result[0] != "sys_config":
                    res = {}
                    res['id'] = i
                    res['all'] = ""
                    res['select'] = ""
                    res['update'] = ""
                    res['insert'] = ""
                    res['delete'] = ""
                    res['drop'] = ""
                    res['index'] = ""
                    res['alter'] = ""
                    res['table'] = result[0]
                    tablelist.remove(result[0])
                    privlist = result[1].split(',')
                    for priv in privlist:
                        key = priv.lower()
                        if key in res.keys():
                            res[key] = "y"
                    i = i + 1
                    reslists.append(res)
            for table in tablelist:
                res = {}
                res['id'] = i
                i = i + 1
                res['all'] = ""
                res['select'] = ""
                res['update'] = ""
                res['insert'] = ""
                res['delete'] = ""
                res['drop'] = ""
                res['index'] = ""
                res['alter'] = ""
                res['table'] = table
                reslists.append(res)
        else:
            j = 1
            for table in tablelist:
                res = {}
                res['id'] = j
                j = j + 1
                res['all'] = ""
                res['select'] = ""
                res['update'] = ""
                res['insert'] = ""
                res['delete'] = ""
                res['drop'] = ""
                res['index'] = ""
                res['alter'] = ""
                res['table'] = table
                reslists.append(res)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "rows": reslists[start:start+rows],
        "total":len(reslists)
    })
@system.route("/adduser",methods=["GET","POST"])
def adduser():
    name = request.form.get("username")
    password = request.form.get("password")
    key = Config.AESKEY
    encryptpwd = aesEncrypt(key,password)
    realname = request.form.get("realname")
    mail = request.form.get("mail")
    datetimes = datetime.datetime.now().strftime('%Y-%m-%d')
    code = 0
    if name !="" and password !="" and realname !="" and mail !="" and realname!="":
        conn = get_conn()
        cursor = conn.cursor()
        sql = "insert into user (name,password,realname,email,createtime)VALUES('{}','{}','{}','{}','{}')".format(name,encryptpwd,realname,mail,datetimes)
        print(sql)
        try:
            cursor.execute(sql)
            conn.commit()
            code=1
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        code = 0
    return jsonify({
        "code":code
    })
@system.route("/addmysql",methods=["GET","POST"])
def addmysql():
    uid = request.form.get("uid")
    name = request.form.get("addname")
    host = request.form.get("addhost")
    user = request.form.get("adduser")
    password = request.form.get("addpassword")
    key = Config.AESKEY
    encryptpwd = aesEncrypt(key,password)
    port = request.form.get("adddatabase")
    conn = get_conn()
    cursor = conn.cursor()
    code = 0
    jiaoyansql = "select a.alias,a.`host`,a.root,a.`password`,a.`port`,a.uid from dbconfig as a where a.alias='{}' and a.`host`='{}' and a.root='{}' and a.`password`='{}' and a.`port`='{}' and uid={}".format(name,host,user,encryptpwd,port,uid)
    try:
        cursor.execute(jiaoyansql)
        jyres= cursor.fetchone()
        if jyres is None:
            sql = "insert into dbconfig (alias,`host`,root,`password`,`port`,isconn,uid)values('{}','{}','{}','{}','{}',{})".format(name,host,user,encryptpwd,port,0,uid)
            cursor.execute(sql)
            conn.commit()
            code= 1
        else:
            code = 3
    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "code":code
    })
@system.route("/editormysql",methods=["GET","POST"])
def editormysql():
    host = request.form.get("edithost")
    name = request.form.get("editorname")
    user = request.form.get("editoruser")
    password = request.form.get("editorpassword")
    key = Config.AESKEY
    encryptpwd = aesEncrypt(key,password)
    port = request.form.get("editordatabase")
    id = request.form.get("editorid")
    conn = get_conn()
    cursor = conn.cursor()
    code = 0
    try:
        sql = "update dbconfig set alias = '{}',host ='{}',root='{}',password = '{}',port='{}' where sid={}".format(name,host,user,encryptpwd,port,id)
        cursor.execute(sql)
        conn.commit()
        code = 1
    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "code":code
    })
@system.route("/delmysql",methods=["GET","POST"])
def delmysql():
    kid = request.values.get("id")
    user = request.values.get('user')
    host = request.values.get('host')
    vhost = "localhost"
    root = request.values.get('root')
    password = request.values.get('password')
    decryptpwd = aesDecrypt(Config.AESKEY,password)
    port = request.values.get('port')
    msg = ""
    code = 0
    try:
        connection = pymysql.Connection(host=host, user=root, password=decryptpwd, port=int(port))
        cursor2 = connection.cursor()
        if host != "localhost" and host != "127.0.0.1":
            vhost = "%"
        elif host == "127.0.0.1":
            vhost = "127.0.0.1"
        dropsql = "drop user '{}'@'{}'".format(user, vhost)
        # print(dropsql)
        try:
            cursor2.execute(dropsql)
            connection.commit()
            connection = get_conn()
            cursor2 = connection.cursor()
            updatestatus = "update dbconfig set isconn =0 where sid = {}".format(int(kid))
            print(updatestatus)
            try:
                cursor2.execute(updatestatus)
                connection.commit()
                code = 1
            except Exception as e:
                print(e)
                code = 4
        except Exception as e:
            print(e)
            code = 2
            msg = str(e)
        finally:
            cursor2.close()
            connection.close()
    except Exception as e:
        print(e)
        code = 3
    return jsonify({
        "code":code,
        "msg":msg
    })
@system.route("/delmysql2",methods=["GET","POST"])
def delmysql2():
    host = request.values.get('ip')
    # print(host)
    root = request.values.get('root')
    # print(root)
    password = request.values.get('password')
    key = Config.AESKEY
    # print(Config.AESKEY)
    decryptpwd = aesDecrypt(key, password)
    port = int(request.values.get('port'))
    # print(port)
    id = request.values.get('id')
    uid = request.values.get('uid')
    user = request.values.get('user')
    connection = pymysql.Connection(host=host, user=root, password=decryptpwd, port=int(port))
    cursor2 = connection.cursor()
    usql = "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{}')".format(user)
    code = 0
    msg = ""
    try:
        cursor2.execute(usql)
        ures = cursor2.fetchone()
        if ures[0]==1:
            code = 2
        elif ures[0] == 0:
            conn = get_conn()
            cursor = conn.cursor()
            sql = "delete from dbconfig where sid = {} and uid = {}".format(int(id), int(uid))
            try:
                cursor.execute(sql)
                conn.commit()
                code = 1
            except Exception as e:
                print(e)
                msg = str(e)
    except Exception as e:
        print(e)
    return jsonify({
        'code':code,
        'msg':msg
    })
@system.route("/deluser",methods=["GET","POST"])
def deluser():
    id = request.values.get('id')
    uid = int(id)
    conn = get_conn()
    cursor = conn.cursor()
    code = 0
    try:
        sql = "delete from user where uid ={}".format(uid)
        cursor.execute(sql)
        conn.commit()
        code =1
    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        'code':code
    })
@system.route("/login")
def login():
    return render_template("/system/login.html")
@system.route("/checklogin",methods=["GET","POST"])
def checklogin():
    name = request.form.get("name")
    password = request.form.get("password")
    hash1 = hashlib.md5()
    hash1.update(password.encode("utf-8"))
    hashpass = hash1.hexdigest()
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select password from root where root = '{}'".format(name)
    cursor.execute(sql)
    try:
        result = cursor.fetchone()
        url = ""
        if len(result) > 0 and hashpass == result[0]:
            session['root'] = name
            url = "index"
        else:
            url = "login"
    except Exception as e:
        print(e)
        url = "login"
    finally:
        cursor.close()
        conn.close()
    return redirect(url)
@system.route("/register",methods=["GET","POST"])
def register():
    name = request.form.get("name")
    password = request.form.get('password')
    url = ""
    if name is not None and password is not None:
        hash1 = hashlib.md5()
        hash1.update(password.encode("utf-8"))
        hashpass = hash1.hexdigest()
        conn = get_conn()
        cursor = conn.cursor()
        sql = "insert into root (root,password)values('{}','{}')".format(name,hashpass)
        try:
            cursor.execute(sql)
            conn.commit()
            return redirect('login')
        except Exception as e:
            print(e)
            conn.rollback()
            return redirect('register')
        finally:
            cursor.close()
            conn.close()
    else:
        return redirect('register')
@system.route("/userdata")
def userdata():
    return  render_template("/system/userlist.html")
@system.route("/userdatas",methods=["GET","POST"])
def userdatas():
    page = int(request.values.get("page"))
    rows = int(request.values.get('rows'))
    start = (page - 1) * rows
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from user limit {},{}".format(start,rows)
    reslist = []
    total = 0
    try:
        try:
            sql2 = "select count(*) from user"
            cursor.execute(sql2)
            result = cursor.fetchone()
            if len(result)>0:
                total = result[0]
        except Exception as e:
            print(e)
        cursor.execute(sql)
        results = cursor.fetchall()
        # i =1
        for result in results:
            res = {}
            # res["id"] = i
            # i = i+1
            res['uid'] = result[0]
            res['name'] = result[1]
            res['password'] = "********"
            res['realname'] = result[3]
            res['email'] = result[4]
            res['createtime'] = result[5]
            reslist.append(res)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "rows":reslist,
        "total":total
    })
@system.route("/editsourceshow",methods=["GET","POST"])
def editsourceshow():
    id = request.values.get('id')
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from dbconfig where sid = {}".format(id)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        res = {}
        res['sid'] = result[0]
        res['name'] = result[1]
        res['host'] = result[2]
        res['root'] = result[3]
        res['password'] = result[4]
        res['port'] = result[5]
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify(res)
@system.route("/editoruser",methods=["GET","POST"])
def editoruser():
    uid = request.values.get('id')
    conn = get_conn()
    cursor = conn.cursor()
    code = 0
    sql = "select * from user where uid = {}".format(uid)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        res={}
        res['id'] = result[0]
        res['name'] = result[1]
        res['password'] = result[2]
        res['realname'] = result[3]
        res['email'] = result[4]
    except Exception as e:
        print(e)
        code = 2
    finally:
        cursor.close()
        conn.close()
    return jsonify(res)
@system.route("/editor",methods=["GET","POST"])
def editor():
    editorid = request.values.get('editorid')
    editroname = request.values.get('editroname')
    editorpwd = request.values.get('editorpwd')#传输过来的明文密码
    key = Config.AESKEY
    decryptpwd = aesEncrypt(key,editorpwd) #进行加密的密码
    # editorRealname = request.values.get('editorRealname')
    # editoremail = request.values.get('editoremail')
    now_date = datetime.datetime.now()
    nowdate = datetime.datetime.strftime(now_date, '%Y-%m-%d')
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select host,root,password,port  from dbconfig where uid={}".format(editorid)
    code = 0
    msg = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            host = result[0]
            vhost = "localhost"
            root = result[1]
            password = result[2]
            port = result[3]
            if host != "localhost" and host != "127.0.0.1":
                vhost = "%"
            elif host == "127.0.0.1":
                vhost = "127.0.0.1"
            try:
                connection = pymysql.Connection(host=host, user=root, password=password, port=int(port),
                                                database='mysql')
                cursor2 = connection.cursor()
                versionsql = "select version()"
                try:
                    cursor2.execute(versionsql)
                    versionresult = cursor2.fetchone()
                    version = versionresult[0]
                    # print(type(version[0]))
                    sql2 = ""
                    if version[0] == "5":
                        sql2 = "update mysql.user set password=password('{}') where user='{}' and host='{}';".format(
                            editorpwd, editroname, vhost)
                    elif version[0] == "8":
                        sql2 = "alter user '{}'@'{}' IDENTIFIED WITH mysql_native_password BY '{}';".format(editroname,
                                                                                                            vhost,
                                                                                                            editorpwd)
                    # print(sql2)
                    try:
                        cursor2.execute(sql2)
                        connection.commit()
                        sql3 = "update user set password = '{}' ,updatetime = '{}' where uid={}".format(
                            decryptpwd, nowdate, editorid)
                        try:
                            cursor.execute(sql3)
                            conn.commit()
                            code = 1
                        except Exception as e:
                            print(e)
                            coed = 0
                            msg = str(e)
                            conn.rollback()
                        finally:
                            cursor.close()
                            conn.close()
                    except Exception as e:
                        print(e)
                        code = 0
                        connection.rollback()
                except Exception as e:
                    print(e)
                finally:
                    cursor2.close()
                    connection.close()
            except Exception as e:
                print(e)
                code = 2
                msg = str(e)
    except Exception as e:
        print(e)
        code = 0
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "code":code,
        "msg":msg
    })
@system.route("/editorinfo",methods=["GET","POST"])
def editorinfo():
    editorname = request.values.get("editorname")
    editorRealname = request.values.get("editorRealname")
    editoremail = request.values.get("editoremail")
    conn = get_conn()
    cursor = conn.cursor()
    code = 0
    msg = ""
    sql = "update user set realname='{}',email='{}' where name = '{}'".format(editorRealname,editoremail,editorname)
    try:
        cursor.execute(sql)
        conn.commit()
        code = 1
    except Exception as e:
        print(e)
        code = 2
        msg=str(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "code":code,
        "msg":msg
    })
@system.route("/crmysqluser",methods=["GET","POST"])
def crmysqluser():
    kid = request.values.get('kid')
    host = request.values.get('host')
    vhost = "localhost"
    root = request.values.get('root')
    password = request.values.get('password')
    user = request.values.get('user')
    port = request.values.get('port')
    userpwd = request.values.get('pwd')
    key = Config.AESKEY
    decryptpwd = aesDecrypt(key,userpwd)
    rootpwd = aesDecrypt(key,password)
    msg = ""
    code = 0
    try:
        conn = pymysql.Connection(host=host, user=root, password=rootpwd, database='mysql', port=int(port))
        cursor = conn.cursor()
        if host !="localhost" and host !="127.0.0.1":
            vhost = "%"
        elif host =="127.0.0.1":
            vhost = "127.0.0.1"
        isuser = "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{}')".format(user)
        cursor.execute(isuser)
        isu = cursor.fetchone()
        if isu[0] == 0:
            sql = "create user '{}'@'{}' identified by '{}';".format(user, vhost, decryptpwd)
            try:
                cursor.execute(sql)
                connection = get_conn()
                cursor2 = connection.cursor()
                updatestatus = "update dbconfig set isconn =1 where sid = {}".format(kid)
                print(updatestatus)
                try:
                    cursor2.execute(updatestatus)
                    connection.commit()
                    code = 1
                except Exception as e:
                    print(e)
                    code = 4
            except Exception as e:
                print(e)
                msg = str(e)
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
        elif isu[0]==1:
            code = 3
    except Exception as e:
        print(e)
        msg = str(e)
        code= 2
    return jsonify({
        "code": code,
        "msg":msg,
    })
@system.route("/applysqlPage")
def applysqlPage():
    return  render_template("/system/orderapply.html")
@system.route("/orderrecord",methods=["GET","POST"])
def orderrecrd():
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from privsqlrecord order by status asc,id desc"
    resList = []
    total = ""
    try:
        cursor.execute(sql)
        resultList = cursor.fetchall()

        for result in resultList:
            status = ""
            if result[8] == 0:
                status = "待审核"
            if result[8]  == 1:
                status = "通过"
            if result[8]  == 2:
                status = "拒绝"
            res = {}
            res['rid'] = result[0]
            res['uid'] = result[1]
            res['uname'] = result[2]
            res['dbalias'] = result[3]
            res['database'] = result[5]
            res['host'] = result[4]
            res['createtime'] = result[9]
            res['status'] = status
            res['result'] = result[7]
            res['sql'] = result[6]
            resList.append(res)
        sql2 = "select count(*) from privsqlrecord"
        cursor.execute(sql2)
        counts = cursor.fetchone()
        total = counts[0]
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        'rows': resList,
        'total': total
    })
@system.route("/orderok",methods=["GET","POST"])
def orderok():
    rid = request.values.get('rid')
    uid = request.values.get('uid')
    uname = request.values.get('uname')
    database = request.values.get('database')
    host = request.values.get('host')
    sql = request.values.get('sql')
    conn = get_conn()
    cursor = conn.cursor()
    code = 0
    msg = ""
    get_db = "select * from dbconfig where host = '{}' and uid = '{}' ".format(host,uid)
    try:
        cursor.execute(get_db)
        dbconfig = cursor.fetchone()
        host = dbconfig[2]
        root = dbconfig[3]
        password = dbconfig[4]
        key = Config.AESKEY
        decryptpwd = aesDecrypt(key, password)
        print(decryptpwd)
        port = int(dbconfig[5])
        try:
            connection = pymysql.Connection(host=host,user=root,password=decryptpwd,database=database,port=port)
            ccursor2 = connection.cursor()
            ccursor2.execute(sql)
            connection.commit()
            effectRow = ccursor2.rowcount
            update_sql = "update privsqlrecord set result = '{}',status=1 where id = {} ".format(effectRow,rid)
            print(update_sql)
            try:
                cursor.execute(update_sql)
                conn.commit()
                code = 1
            except Exception as e:
                print(e)
                code = 2
                msg = str(e)
            finally:
                ccursor2.close()
                connection.close()
        except Exception as e:
            print(e)
            code = 0
            msg = str(e)
    except Exception as e:
        print(e)
        code = 2
        msg = str(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "code":code,
        "msg":msg
    })
@system.route("/orderno",methods=["GET","POST"])
def orderno():
    id = request.values.get('orderid')
    conn = get_conn()
    cursor = conn.cursor()
    code = 0
    msg = ""
    try:
        cursor.execute("update privsqlrecord set status = 2 where id = {}".format(id))
        conn.commit()
        code = 1
    except Exception as e:
        print(e)
        msg = str(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        'code':code,
        'msg':msg
    })
@system.route("/sysout")
def sysout():
    session.pop('root')
    return redirect('login')
def get_conn():
    conn = pymysql.Connection(host='localhost',user='root',password='root',database='easyui')
    # conn = pymysql.Connection(host='10.2.13.251', user='ps_db_mgr', password='Credit#ps_db_mgr123',database='ps_db_mgr')
    return conn

