import datetime
from flask import render_template, redirect, request,jsonify, session
from . import index
import pymysql
from ..AES import aesEncrypt,aesDecrypt
from python.config import Config
from python.app.ado.mysqlAdo import DBHelper
@index.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
@index.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500
@index.route("/login")
def login():
    return render_template("/index/login.html")
@index.route("/checklogin",methods=["GET","POST"])
def checklogin():
    name = request.values.get("name").strip()
    password = request.values.get("pass").strip()
    key = Config.AESKEY
    encryptpwd = aesEncrypt(key,password)
    url = "login"
    if name is not None and password is not None:
        conn = get_conn()
        cursor = conn.cursor()
        sql = "select password,uid from user where name ='{}'".format(name)
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            # print(result[0])
            if  encryptpwd == result[0]:
                session['user'] = name
                session['uid'] = result[1]
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
@index.route("/permision",methods=["GET","POST"])
def permision():
    return render_template("/index/permision.html")
@index.route("/dbconfig",methods=["GET","POST"])
def dbconfig():
    uid = session.get('uid')
    # print(uid)
    conn =  get_conn()
    cursor = conn.cursor()
    sql = "select * from dbconfig where uid={}".format(uid)
    reslist = []
    key = Config.AESKEY
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            res = {}
            res['kid'] = result[0]
            res['name'] = result[1]
            res['host'] = result[2]
            res['user'] = result[3]
            res['password'] = result[4]
            res['password2'] = "******"
            res['port'] = result[5]
            if result[6]==1:
                res['isconn'] = "已关联"
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
@index.route("/dblist",methods=["GET","POST"])
def dblist():
    host = request.values.get('host')
    root = request.values.get('root')
    password = request.values.get('password')
    key = Config.AESKEY
    decryptpwd = aesDecrypt(key, password)
    # print(decryptpwd)
    port = request.values.get('port')
    reslist = []
    try:
        conn = pymysql.Connection(host=host, user=root, password=decryptpwd, port=int(port))
        cursor = conn.cursor()
        sql = "show databases"
        try:
            cursor.execute(sql)
            datas = cursor.fetchall()
            for data in datas:
                res = {}
                if data[0] != "information_schema" and data[0] != "mysql" and data[0] != "sys" and data[
                    0] != "performance_schema":
                    res['database'] = data[0]
                    reslist.append(res)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(e)
    return jsonify({
        "rows": reslist
    })
@index.route("/tablelist",methods=["GET","POST"])
def tablelist():
    username = session.get('user')
    page = int(request.values.get('page'))
    rows2 = int(request.values.get('rows'))
    start2 = (page - 1) * rows2
    host = request.values.get('host')
    vhost = "localhost"
    root = request.values.get('root')
    user = session.get('user')
    password = request.values.get('password')
    key = Config.AESKEY
    decryptpwd = aesDecrypt(key,password)
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
    tablecursor.close()
    conn.close()
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
    try:
        cursor.execute(sql2)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
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
        j=1
        for table in tablelist:
            res = {}
            res['id'] =j
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
    return jsonify({
        "rows": reslists[start2:start2+rows2],
        'total':len(reslists)
    })
@index.route("/applytable")
def applytable():
    pass
@index.route("/gettables",methods=["GET","POST"])
def gettables():
    host = request.values.get("host")
    database = request.values.get("database")
    user = request.values.get("user")
    password = request.values.get("password")
    port = request.values.get("port")
    conn = pymysql.Connection(host=host,user=user,password=password,port=int(port))
    cursor = conn.cursor()
    sql = "SELECT table_name FROM information_schema.TABLES where TABLE_SCHEMA='{}'".format(database)
    reslist = []
    code = 0
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        code = 1
        if len(results)>0:
            for result in results:
                reslist.append(result[0])
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "rows":reslist,
        "total":len(reslist),
        "code":code
    })
@index.route("/applyfor",methods=["GET","POST"])
def applyfor():
    #申请状态 0 表示待审核 1 表示审核通过 2 表示审核拒绝
    user = session.get('user')
    uid = session.get('uid')
    list = request.values.getlist('list[]')
    host = request.values.get('host')
    alias = request.values.get('alias')
    database = request.values.get('database')
    table = request.values.get('table')
    expire = request.values.get('expire')
    if expire =="":
        dieline = ''
    else:
        dieline = (datetime.datetime.now() + datetime.timedelta(days=float(expire))).strftime("%Y-%m-%d %H:%M:%S")
    priv = ",".join(list)
    status = 0
    code = 0
    now_date = datetime.datetime.now()
    nowdata = datetime.datetime.strftime(now_date, '%Y-%m-%d')
    conn  = get_conn()
    cursor = conn.cursor()
    sql = "insert into applymsg (uid,uname,db,dbstatus,createtime,dbalias,ip,utable,privilege,expire)values" \
          "({},'{}','{}',{},'{}','{}','{}','{}','{}','{}')".format(uid,user,database,status,nowdata,alias,host,table,priv,dieline)
    # print(sql)
    try:
        cursor.execute(sql)
        conn.commit()
        code = 1
    except Exception as e:
        print(e)
        code = 2
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return jsonify({
        "code":code
    })
@index.route("/applyrecord")
def applyrecord():
    return render_template("/index/applyrecord.html")
@index.route("/recordlist",methods=["GET","POST"])
def recordlist():
    username = session.get('user')
    page = int(request.values.get('page'))
    rows = int(request.values.get('rows'))
    start = (page - 1) * rows
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from applymsg where uname = '{}' order by dbstatus asc ,id desc  limit {},{} ".format(username,start,rows)
    # print(sql)
    sql2 = "select count(*) from applymsg where uname = '{}'".format(username)
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
                res['dbalias'] = result[7]
                res['host'] = result[8]
                res['database'] = result[3]
                res['table'] = result[9]
                if result[10] == "all":
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
@index.route("/orderapply",methods=["GET","POST"])
def orderapply():
    database = request.values.get('targetDb')
    host = request.values.get('targethost')
    alias = request.values.get('targetDbName')
    now_date = datetime.datetime.now()
    now_time = datetime.datetime.strftime(now_date, '%Y-%m-%d')
    code = 0
    uid = session.get('uid')
    name = session.get('user')
    try:
        conn = get_conn()
        cursor = conn.cursor()
        sqlString = request.values.get('sql')
        print(sqlString)
        if ';' in sqlString:
            sqlList = sqlString.split(';')
            sqlList.pop(len(sqlList)-1)
            for sqlstr in sqlList:
                insert_sql = "insert into privsqlrecord (uid,uname,alias,ip,db,strsql,status,createtime)values('%s','%s','%s','%s','%s',\"%s\",%s,'%s')" %(uid,name,alias,host,database,sqlstr,0,now_time)
                # print(insert_sql)
                try:
                    cursor.execute(insert_sql)
                    conn.commit()
                    code = 1
                except Exception as e:
                    print(e)
                    code = 2
        else:
            code = 3
    except Exception as e:
        print(e)
    res = {
        'code':code,
    }
    return jsonify(res)
@index.route("/sysout")
def sysout():
    session.pop('user')
    return redirect('login')
@index.route("/orderapplyrecord")
def orderapplyrecord():
    return render_template("/index/orderapply.html")

@index.route("/orderrecord",methods=["GET","POST"])
def orderrecord():
    uid = session.get('uid')
    page = int(request.values.get('page'))
    rows = int(request.values.get('rows'))
    start = (page - 1) * rows
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from privsqlrecord  where uid ={} order by status asc,id desc ".format(int(uid))
    try:
        cursor.execute(sql)
        resultList = cursor.fetchall()
        resList = []
        for result in resultList:
            status = ""
            if result[8] == 0:
                status = "待审核"
            if result[8] == 1:
                status = "通过"
            if result[8] == 2:
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
            res['sql'] = result[6]
            res['result'] = result[7]
            resList.append(res)
        sql2 = "select count(*) from privsqlrecord where uid ={} limit {},{} ".format(uid,start,rows)
        cursor.execute(sql2)
        counts = cursor.fetchone()
        total = counts[0]
        return jsonify({
            'rows': resList,
            'total': total
        })
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
@index.route('/index',methods=["GET","POST"])
def index():
    user = session.get('user')
    if user is None:
        return  render_template("/index/login.html")
    else:
        return render_template('/index/index.html',user=user)
def get_conn():
    conn = pymysql.Connection(host='localhost',user='root',password='root',database='easyui')
    # conn = pymysql.Connection(host='10.2.13.251', user='ps_db_mgr', password='Credit#ps_db_mgr123', database='ps_db_mgr')
    return conn