import os
from re import escape
from flask import Flask, render_template, redirect, session, flash, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from database import accion, seleccion, seleccionSecure

from forms import Login, Registro, Producto, EditarP
from utils import email_valido, pass_valido 


app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/", methods= ["GET"])
def inicio():
  return render_template('index.html')

@app.route("/productos", methods= ["GET"])
def productos():
    return render_template("product-list.html")

@app.route("/listadeseos", methods= ["GET", "POST"])
def lista_deseos():
    try:
        sql = 'SELECT wl.WishListID, wl.ProductID, p.nombre_pro, p.precio_venta, p.tipo_pro FROM WishList as wl INNER JOIN productos AS p on wl.ProductID = p.id_producto WHERE wl.UserID=?'
        res = seleccionSecure(sql, str(session['id_usuario']))
        if len(res)==0:
            flash('No se encontraron productos en la lista de deseos')
        return render_template("listadeseos.html", data=res)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        flash('La sesión actual ha terminado. Debe iniciar sesión nuevamente', 'danger')
        return redirect('/login')

        
@app.route("/clearWishListItem/<idItem>", methods= ["POST"])
def clearWishListItem(idItem):
    sql = 'DELETE FROM WishList where WishListID=?'
    res = accion(sql, idItem)
    return sql;

@app.route("/queryWishList", methods= ["POST"])
def queryWishList():
    try:
        aItems = request.json
        sSelected = ''
        for item in aItems:
            sSelected += item +', ' 
        if len(sSelected) == 0:
            sql = f'SELECT id_producto, nombre_pro, tipo_pro, cantidad, precio_venta, descripcion FROM productos'
        else:
            sql = f'SELECT id_producto, nombre_pro, tipo_pro, cantidad, precio_venta, descripcion FROM productos WHERE id_producto not in({sSelected[0:len(sSelected)-2]})'
        res = seleccion(sql)
        return jsonify(res)

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        flash('La sesión actual ha terminado. Debe iniciar sesión nuevamente', 'danger')
        # return redirect('/login')
        return jsonify({error: 'algo pasó'})
    
@app.route("/addWishProduct", methods= ["POST"])
def addWishProduct():
    try:
        oItem = request.json
        sql = 'SELECT max(WishListID) FROM WishList'
        res = seleccion(sql)
        idUser = session['id_usuario']
        if res[0][0] is None:
            nextId = 1
        else:
            nextId = int(res[0][0])+1
        sqlInsert = f"INSERT INTO WishList ( WishListID, UserID, ProductID, WLDate) VALUES (?, ?, ?, CURRENT_TIMESTAMP)"

        resInsert = accion(sqlInsert,(nextId, idUser, oItem['id']))

        # return jsonify({"data": "t"})
        return jsonify({"data": resInsert})

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        flash('Fallo al llamar endpoint addWishProduct')
        # return redirect('/login')
        return jsonify({"error": 'algo pasó'})

@app.route("/carcompras", methods= ["GET","POST"])
def car_compras():
    return render_template("cart.html")

@app.route("/registro", methods=["GET", "POST"] )
def registro():
    form = Registro()
    if  request.method == "GET": #Si la ruta es accedida a través del método GET entonces
	    return render_template('register.html', form=form,titulo=' ')
    else:
        # Recuperar los datos del formulario
        nom = escape(request.form['nombre'])
        ape = escape(request.form['apellido'])
        ema = (request.form['email'])
        tel = escape(request.form['telefono'])
        tipo_id = escape(request.form['tipo_ide'])
        num_ide = escape(request.form['num_ide'])
        pa = escape(request.form['pais'])
        dep = escape(request.form['departamento'])
        ciu = escape(request.form['ciudad'])
        dir = escape(request.form['direccion'])
        fec_naci = escape(request.form['fecha_naci'])
        con = escape(request.form['contrasena'])
        ver = escape(request.form['val_cont'])
        ter = escape(request.form['Condition'])
        prom = escape(request.form['promocional'])
        tip_user= 'user_final'

        swerror = False
        if nom==None or len(nom)==0:
            flash('ERROR: Debe suministrar un Nombre')
            swerror = True
        if ape==None or len(ape)==0 :
            flash('ERROR: Debe suministrar un Apellido ')
            swerror = True
        if ema==None or len(ema)==0 or not email_valido(ema):
            flash('ERROR: Debe Suministrar un Email válido')
            swerror = True
        if tel==None or len(tel)==0:
            flash('ERROR: Debe Suministrar un Número de Telefono')
            swerror = True
        if tipo_id==None or len(tipo_id)==0:
            flash('ERROR: Debe Escojer un Tipo de Documento')
            swerror = True
        if num_ide==None or len(num_ide)==0:
            flash('ERROR: Debe Suministrar un Numero de Documento')
            swerror = True
        if pa==None or len(pa)==0:
            flash('ERROR: Debe Escojer un Pais')
            swerror = True
        if dep==None or len(dep)==0:
            flash('ERROR: Debe Suministrar un Departamento')
            swerror = True
        if ciu==None or len(ciu)==0:
            flash('ERROR: Debe una Ciudad')
            swerror = True
        if dir==None or len(dir)==0:
            flash('ERROR: Debe Suministrar una Direccion')
            swerror = True
        if fec_naci==None or len(fec_naci)==0:
            flash('ERROR: Debe Suministrar una Fecha de Nacimiento')
            swerror = True
        if con==None or len(con)==0 or not pass_valido(con):
            flash('ERROR: Debe suministrar una clave válida')
            swerror = True
        if ver==None or len(ver)==0 or not pass_valido(ver):
            flash('ERROR: Debe suministrar una verificación de clave válida')
            swerror = True
        if con!=ver:
            flash('ERROR: La clave y la verificación no coinciden')
            swerror = True
        if not swerror:
            sql = "INSERT INTO PERSONAS(nombre, apellido, email, telefono, tipo_id, num_id, pais, departamento, ciudad, direccion, fecha_naci, condition, promocional) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

            res = accion(sql,(nom, ape, ema, tel, tipo_id, num_ide, pa, dep, ciu, dir, fec_naci, ter, prom))
            if res!=0:
                flash('INFO: Datos almacenados con exito en PERSONA')
            else:
                flash('ERROR EN PERSONA: Por favor reintente')
              
            sql = "INSERT INTO USUARIOS(nickname, contrasena, tipo_user) VALUES (?,?,?)"
            pwd = generate_password_hash(con)
            res= accion(sql,(ema, pwd, tip_user))
            if res!=0:
                flash('INFO: Datos almacenados con exito EN USUARIO')
            else:
                flash('ERROR USUARIO: Por favor reintente')

        return render_template('register.html', form=form, titulo=' ')



@app.route("/login", methods=["GET","POST"])
def login():
    form = Login()
    if  request.method == "GET": #Si la ruta es accedida a través del método GET entonces
	    return render_template('login.html', form=form,titulo=' ')
    else:
     ema = (request.form['email'])
     con = escape(request.form['contrasena'])

    sql = f'SELECT u.id_usuario, u.nickname, u.contrasena, u.tipo_user, p.nombre FROM usuarios as u inner join personas as p on u.nickname= p.email WHERE u.nickname= "{ema}"'
    res = seleccion(sql)
    if len(res)==0:
        flash('ERROR: Usuario o clave invalidas')
        return render_template("login.html", form=form, titulo= " ")
    else:
        cbd = res[0][2]
        if check_password_hash(cbd, con):
            session.clear()
            session['id_usuario'] = res[0][0]
            session['nickname'] = ema
            session['contrasena'] = con
            session['tipo_user'] = res[0][3]
            session['nombre'] = res[0][4]

<<<<<<< HEAD
            if session['tipo_user']== 'user_final':
               return render_template('indexuser.html',form=form, titulo= f"{session['nombre']}", messages =res) 
            if session['tipo_user']==  'user_admin' or 'user_superadmin':
                return render_template('loginadmin.html')
=======
            if session['tipo_user']== 'user_admin':
                return render_template('dashboardn.html',form=form, titulo= f"Bienvenido {session['nombre']}", messages =res)
>>>>>>> a3dfd09175729174706e4dcbfefc031ddb0fba17
            else:
                return render_template('indexuser.html',form=form, titulo= f"Bienvenido {session['nombre']}", messages =res)
        else:
            flash('ERROR: Usuario o clave invalidas')
        return render_template('login.html', form=form, titulo=' ')





@app.route("/soporte", methods= ["GET", "POST"])
def soporte():
    return render_template("soporte.html")

@app.route("/contacto", methods=[ "GET","POST"])
def contacto():
    return render_template("contact.html")

@app.route("/administrador", methods=[ "GET","POST"])
def administrador():
<<<<<<< HEAD
    global tipo_user
    global sesion_iniciada
    global id_usuario_califica
    if  request.method == "GET":
      return render_template('loginadmin.html')
    else:
         ema = (request.form['email'])
         con = escape(request.form['contrasena'])
         
         sql = f'SELECT u.id_usuario, u.nickname, u.contrasena, u.tipo_user, p.nombre FROM usuarios as u inner join personas as p on u.nickname= p.email WHERE u.nickname= "{ema}"'
         res = seleccion(sql)
    if len(res)==0:
        flash('ERROR: Usuario o clave invalidas')
        return render_template("loginadmin.html", form=form, titulo= " ")
    else:
        cbd = res[0][2]
        if check_password_hash(cbd, con):
             session.clear()
             session['id_usuario'] = res[0][0]
             session['nickname'] = ema
             session['contrasena'] = con
             session['tipo_user'] = res[0][3]
             session['nombre'] = res[0][4]
             id_usuario_califica = res[0][0]
             sesion_iniciada= True
             tipo_user = res[0][3]
        if session['tipo_user']== 'user_admin':
                return render_template('dashboardn.html', titulo= f"¡Bienvenido {session['nombre']}!", messages =res)
        if session['tipo_user']== 'user_superadmin':
                return render_template('superdashboardn.html', titulo= f"¡Bienvenido {session['nombre']}!", messages =res)
        else:
            flash('ERROR: Usuario o clave invalidas')
        return render_template('loginadmin.html')



=======
     return render_template('login.html')
>>>>>>> a3dfd09175729174706e4dcbfefc031ddb0fba17

@app.route("/dash", methods=[ "GET","POST"])
def dash():
     return render_template('dashboardn.html')

@app.route("/agregarP", methods=[ "GET","POST"])
def agregarP():
    form = Producto()
    if  request.method == "GET": #Si la ruta es accedida a través del método GET entonces
	    return render_template('agregarprod.html', form=form,titulo=' ')
    else:
        # Recuperar los datos del formulario
        nom = escape(request.form['nom_prod'])
        tipo_p = escape(request.form['tipo_p'])
        can = escape(request.form['cantidad_p'])
        canmin = escape(request.form['can_min'])
        canmax= escape(request.form['can_max'])
        pre = escape(request.form['pre_ven'])
        cali = escape(request.form['cal_pro'])
        des = escape(request.form['descri'])

        swerror = False
        if nom==None or len(nom)==0:
            flash('ERROR: Debe suministrar un Nombre')
            swerror = True
        if tipo_p==None or len(tipo_p)==0 :
            flash('ERROR: Debe suministrar un Tipo de Producto')
            swerror = True
        swerror = False
        if can==None or len(can)==0:
            flash('ERROR: Debe suministrar una Cantidad')
            swerror = True
        if canmin==None or len(canmin)==0 :
            flash('ERROR: Debe suministrar un cantidad minima ')
            swerror = True
        swerror = False
        if canmax==None or len(canmax)==0:
            flash('ERROR: Debe suministrar una canitdad maxima')
            swerror = True
        if pre==None or len(pre)==0 :
            flash('ERROR: Debe suministrar un Precio ')
            swerror = True
        swerror = False
        if cali==None or len(cali)==0:
            flash('ERROR: Debe suministrar una calificacion')
            swerror = True
        if des==None or len(des)==0 :
            flash('ERROR: Debe suministrar una descripcion ')
            swerror = True
        if not swerror:
            sql = "INSERT INTO PRODUCTOS(nombre_pro, tipo_pro, cantidad, cantidad_min, cantidad_max, precio_venta, calificacion, descripcion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

            res = accion(sql,(nom, tipo_p, can, canmin, canmax, pre, cali, des))
            if res!=0:
                flash('INFO: Datos almacenados con exito en PRODUCTO')
            else:
                flash('ERROR EN PRODUCTO: Por favor reintente')

    return render_template("agregarprod.html")




@app.route("/editarP", methods=[ "GET","POST"])
def editarP():
    form = EditarP()
    if  request.method == "GET": #Si la ruta es accedida a través del método GET entonces
	    return render_template('editP.html', form=form,titulo=' ')
    else:
     id = escape(request.form['id_p'])

    sql = f'SELECT id_producto, nombre_pro, tipo_pro, cantidad, cantidad_min, cantidad_max, precio_venta, calificacion, descripcion FROM productos WHERE id_producto = "{id}"'
    res = seleccion(sql)
    if len(res)==0:
        flash('ERROR: Codigo Incorrecto')
        return render_template("editP.html", form=form, titulo= " ")
    else:
        #cbd = res[0][0]
       # if check_password_hash(cbd, id):
            session.clear()
            session['id_producto'] = id
            session['nombre_pro'] = res[0][1]
            session['tipo_pro'] = res[0][2]
            session['cantidad'] = res[0][3]
            session['cantidad_min'] = res[0][4]
            session['cantidad_max'] = res[0][5]
            session['precio_venta'] = res[0][6]
            session['calificacion'] = res[0][7]
            session['descripcion'] = res[0][8]
    
<<<<<<< HEAD
            flash(' Producto Encontrado')
            return render_template("updateP.html", res=res, messages =res)

@app.route("/updatepro", methods=[ "GET","POST"])
def updatepro():
    global tipo_user
    form = Productoedit()
    if  request.method == "POST": 
	  
        # Recuperar los datos del formulario
        nom = (request.form['nom_prod'])
        #id = session['id_producto']
        id = (request.form['id_producto'])
        tipo_p = (request.form['tipo_pro'])
        can = (escape(request.form['cantidad_p']))
        canmin = (escape(request.form['can_min']))
        canmax= (escape(request.form['can_max']))
        pre = (escape(request.form['pre_ven']))
        des = (request.form['descri'])

        sql = f"UPDATE productos SET nombre_pro='{nom}', tipo_pro='{tipo_p}', cantidad='{can}', cantidad_min='{canmin}', cantidad_max='{canmax}', precio_venta='{pre}', descripcion='{des}' WHERE id_producto='{id}'"

        res = seleccion(sql)
        if res!=0:
            flash('INFO: Datos actualizados con exito en PRODUCTO')
        else:
         flash('ERROR EN PRODUCTO: Por favor reintente')
        if tipo_user == 'user_superadmin':
            return render_template('superdashboardn.html')
        else:
             return render_template('dashboardn.html')

@app.route("/deleteP", methods=[ "GET","POST"])
def deleteP():
    form = EditarP()
    if  request.method == "GET": #Si la ruta es accedida a través del método GET entonces
	    return render_template('deletep.html', form=form,titulo=' ')
    else:
     id = escape(request.form['id_p'])

    sql = f'DELETE FROM productos WHERE id_producto = "{id}"'
    res = seleccion(sql)
    if len(res)==0:
        flash(' Producto Eliminado')
        return render_template("deletep.html", form=form, titulo= " ")
    else:
     flash('ERROR: Codigo Incorrecto')
    return render_template("deletep.html", form=form, titulo= " ")



@app.route("/calproducto", methods=[ "GET","POST"])
def calproducto():
    global id_usuario_califica
    global id_producto
    if  request.method == "GET":
        return render_template("calproducto.html", titulo= f"¡Hola {id_usuario_califica}!" )
    else:
        cali = (request.form['cal_pro'])
        id_p= (request.form['id_producto'])
        sql = "INSERT INTO ScoreProduct(User_ID, ProductID, Score,) VALUES (?,?,?)"

        res = accion(sql,(id_usuario_califica,id_p,cali))
        if res!=0:
           flash('INFO: Calificacion Exitosa PRODUCTO')
            
        else:
                flash('ERROR EN PRODUCTO: Por favor reintente')

    return render_template("calproducto.html", res=res, titulo= f"Producto Calificado", messages =res)


@app.route("/addadmin", methods= ["GET", "POST"])
def addadmin():
    form = Registro()
=======
            flash('ERROR: Producto Encontrado')
            return render_template("editP.html", res=res, titulo= f"Bienvenido {session['calificacion']}", messages =res)

@app.route("/updatepro", methods=[ "GET","POST"])
def updatepro():
    form = Producto()
>>>>>>> a3dfd09175729174706e4dcbfefc031ddb0fba17
    if  request.method == "GET": #Si la ruta es accedida a través del método GET entonces
	    return render_template('editarP.html', form=form,titulo=' ')
    else:
        # Recuperar los datos del formulario
        nom = escape(request.form['nom_prod'])
        id = (request.form['id_producto'])
        tipo_p = escape(request.form['tipo_p'])
        can = escape(request.form['cantidad_p'])
        canmin = escape(request.form['can_min'])
        canmax= escape(request.form['can_max'])
        pre = escape(request.form['pre_ven'])
        des = escape(request.form['descri'])

        swerror = False
        if nom==None or len(nom)==0:
            flash('ERROR: Debe suministrar un Nombre')
            swerror = True
        if tipo_p==None or len(tipo_p)==0 :
            flash('ERROR: Debe suministrar un Tipo de Producto')
            swerror = True
        swerror = False
        if can==None or len(can)==0:
            flash('ERROR: Debe suministrar una Cantidad')
            swerror = True
        if canmin==None or len(canmin)==0 :
            flash('ERROR: Debe suministrar un cantidad minima ')
            swerror = True
        swerror = False
        if canmax==None or len(canmax)==0:
            flash('ERROR: Debe suministrar una canitdad maxima')
            swerror = True
        if pre==None or len(pre)==0 :
            flash('ERROR: Debe suministrar un Precio ')
            swerror = True
        swerror = False
        if des==None or len(des)==0 :
            flash('ERROR: Debe suministrar una descripcion ')
            swerror = True
        if not swerror:
            sql = f"update productos set nombre_pro= '{nom}', tipo_pro= '{tipo_p}', cantidad= '{can}', cantidad_min= '{canmin}', cantidad_max= '{canmax}', precio_venta = '{pre}', descripcion='{des}' where id_producto='{id}'"

            res = seleccion(sql)
            if res!=0:
                flash('INFO: Datos actualizados con exito en PRODUCTO')
            else:
<<<<<<< HEAD
                flash('ERROR EN PERSONA: Por favor reintente')
              
            sql = "INSERT INTO USUARIOS(nickname, contrasena, tipo_user) VALUES (?,?,?)"
            pwd = generate_password_hash(con)
            res= accion(sql,(ema, pwd, tip_user))
            if res!=0:
                flash('INFO: Datos almacenados con exito EN USUARIO')
            else:
                flash('ERROR USUARIO: Por favor reintente')

        return render_template('agregaradmin.html', form=form, titulo=' ')


@app.route("/editadmin", methods=[ "GET","POST"])
def editadmin():
    if  request.method == "GET": #Si la ruta es accedida a través del método GET entonces
	    return render_template('editaruser.html', form=form,titulo=' ')
    else:
     id = escape(request.form['id_p'])

    sql = f'SELECT p.id_persona, p.nombre, p.apellido, p.email, p.telefono, p.tipo_id, p.num_id, u.tipo_user FROM personas as p inner join usuarios as u on p.email= u.nickname WHERE id_persona = "{id}"'
    res = seleccion(sql)
    if len(res)==0:
        flash('ERROR: Codigo Incorrecto')
        return render_template("editaruser.html", titulo= " ")
    else:
        #cbd = res[0][0]
       # if check_password_hash(cbd, id):
            session.clear()
            session['id_persona'] = res[0][0]
            session['nombre'] = res[0][1]
            session['apellido'] = res[0][2]
            session['email'] = res[0][3]
            session['telefono'] = res[0][4]
            session['tipo_id'] = res[0][5]
            session['num_id'] = res[0][6]
            session['tipo_user'] = res[0][7]
            
    
            flash(' Usuario Encontrado')
            return render_template("updateuser.html", res=res, messages =res)

@app.route("/updateuser", methods=[ "GET","POST"])
def updateuser():
    global tipo_user
    form = Productoedit()
    if  request.method == "POST": 
	  
        # Recuperar los datos del formulario
        id = (request.form['id_p'])
        nom = (request.form['nombre'])
        ape = (request.form['apellido'])
        ema = (escape(request.form['email']))
        tel = (escape(request.form['telefono']))
        tipo_doc= (escape(request.form['tipo_ide']))
        num_ide = (escape(request.form['num_ide']))
        tip_user = (request.form['tipo_user'])

        sql = f"UPDATE personas SET nombre='{nom}', apellido='{ape}', email='{ema}', telefono='{tel}', tipo_id='{tipo_doc}', num_ide='{num_ide}' WHERE id_persona='{id}'"

        res = seleccion(sql)
        if res!=0:
            flash('INFO: Datos actualizados con exito en PRODUCTO')
        else:
         flash('ERROR EN PERSONA: Por favor reintente')
        
        sql = f"UPDATE usuarios SET tipo_user='{tip_user}' WHERE id_usuarios='{id}'"
        res = seleccion(sql)
        if res!=0:
            flash('INFO: Datos actualizados con exito')
        else:
         flash('ERROR EN PERSONA: Por favor reintente')
        if tipo_user == 'user_superadmin':
            return render_template('superdashboardn.html')
        

@app.route("/listaruserfinal", methods= ["GET"])
def listaruserfinal():
    tipo_user= 'user_final'
    sql = f'SELECT p.*  FROM personas as p join usuarios as u on p.email =u.nickname where u.tipo_user="{tipo_user}" '
    res = seleccion(sql)
    return render_template("listaruserfinal.html", res=res)
   
=======
                flash('ERROR EN PRODUCTO: Por favor reintente')
>>>>>>> a3dfd09175729174706e4dcbfefc031ddb0fba17

    return render_template('editarP.html', form=form,titulo=' ')




@app.route("/calproducto", methods=[ "GET","POST"])
def calproducto():
    return render_template("calproducto.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')








    
