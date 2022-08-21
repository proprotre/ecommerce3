from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask import redirect
from flask_login import(current_user, LoginManager, login_user, logout_user, login_required)
import hashlib

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://proprotre1:toledo321654@proprotre1.mysql.pythonanywhere-services.com:3306/proprotre1$sonegocio"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.secret_key= "123456"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view= "login"

class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column("idusuario", db.Integer, primary_key=True)
    nome = db.Column("user_nome", db.String(256))
    email = db.Column("user_email", db.String(256))
    senha = db.Column("user_senha", db.String(256))
    end = db.Column("user_end", db.String(256))
    telefone = db.Column("user_telefone", db.String(256))

    def __init__(self, nome, email, senha, end, telefone):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.end = end
        self.telefone = telefone

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Favorito(db.Model):
    __tablename__ = "favorito"
    id = db.Column("idfavorito", db.Integer, primary_key=True)
    idanuncio = db.Column("anunc_idanuncio", db.Integer, db.ForeignKey("anuncio.idanuncio"))
    idusuario = db.Column("user_idusuario", db.Integer, db.ForeignKey("usuario.idusuario"))

    def __init__(self, idanuncio, idusuario):
        self.idanuncio = idanuncio
        self.idusuario = idusuario

class Compra(db.Model):
    __tablename__ = "compra"
    id = db.Column("idcompra", db.Integer, primary_key=True)
    preco = db.Column("com_preco", db.Float)
    qtd = db.Column("com_qtd", db.Integer)
    total = db.Column("com_total", db.Float)
    idanuncio = db.Column("anunc_idanuncio", db.Integer, db.ForeignKey("anuncio.idanuncio"))
    idusuario = db.Column("user_idusuario", db.Integer, db.ForeignKey("usuario.idusuario"))

    def __init__(self, preco, qtd, total, idanuncio, idusuario):
        self.preco = preco
        self.qtd = qtd
        self.total = total
        self.idanuncio = idanuncio
        self.idusuario = idusuario

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column("idcategoria", db.Integer, primary_key=True)
    nome = db.Column("cat_nome", db.String(256))
    desc = db.Column("cat_desc", db.String(256))

    def __init__(self, nome, desc):
        self.nome = nome
        self.desc = desc

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column("idanuncio", db.Integer, primary_key=True)
    nome = db.Column("anunc_nome", db.String(256))
    desc = db.Column("anunc_desc", db.String(256))
    qtd = db.Column("anunc_qtd", db.Integer)
    preco = db.Column("anunc_preco", db.Float)
    idusuario = db.Column("user_idusuario", db.Integer, db.ForeignKey("usuario.idusuario"))
    idcategoria = db.Column("cat_idcategoria", db.Integer, db.ForeignKey("categoria.idcategoria"))

    def __init__(self, nome, desc, qtd, preco, idusuario, idcategoria):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.idusuario = idusuario
        self.idcategoria = idcategoria

class Pergunta(db.Model):
    __tablename__ = "pergunta"
    id = db.Column("idPergunta", db.Integer, primary_key=True)
    pergunta = db.Column("per_pergunta", db.String(256))
    resposta = db.Column("per_resposta", db.String(256))
    idusuario = db.Column("user_idusuario", db.Integer, db.ForeignKey("usuario.idusuario"))
    idanuncio = db.Column("anunc_idanuncio", db.Integer, db.ForeignKey("anuncio.idanuncio"))

    def __init__(self, pergunta, resposta, idusuario, idanuncio):
        self.pergunta = pergunta
        self.resposta = resposta
        self.idusuario = idusuario
        self.idanuncio = idanuncio

def loginMenu():
    if request.method == "POST":
        email = request.form.get("email")
        passwd = hashlib.sha512(str(request.form.get("passwd")).encode("utf-8")).hexdigest()
        user = Usuario.query.filter_by(email = email, senha = passwd).first()
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))

def validaLogin(id):
    if current_user.id == id:
        return True
    elif current_user.id == 1:
        return True
    else:
        return False

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template("error404.html")

@app.errorhandler(500)
def paginanaoencontrada(error):
    return render_template("error500.html")

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        passwd = hashlib.sha512(str(request.form.get("passwd")).encode("utf-8")).hexdigest()
        user = Usuario.query.filter_by(email = email, senha = passwd).first()
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    return render_template("login.html", titulo="Faça Login")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/")
def index():
    db.create_all()
    loginMenu()
    return render_template("index.html", usuarios = Usuario.query.all(), anuncios = Anuncio.query.all(), categorias = Categoria.query.all())

@app.route("/cad/categoria/")
@login_required
def categoria():
    if current_user.id == 1:
        return render_template("categoria.html", categorias = Categoria.query.all(), titulo="Cadastro de Categoria")
    else:
        return redirect(url_for("index"))

@app.route("/categoria/criar", methods=["POST"])
@login_required
def criarcategoria():
    if current_user.id == 1:
        categoria = Categoria(request.form.get("nome"), request.form.get("desc"))
        db.session.add(categoria)
        db.session.commit()
        return redirect(url_for("categoria"))
    else:
        return redirect(url_for("index"))

@app.route("/categoria/detalhar/<int:id>")
@login_required
def buscarcategoria(id):
    if current_user.id == 1:
        return render_template("cat_detalhes.html", categorias = Categoria.query.get(id), anuncio = Anuncio.query.all())
    else:
        return redirect(url_for("index"))

@app.route("/categoria/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editarcategoria(id):
    categoria = Categoria.query.get(id)
    if current_user.id == 1:
        if request.method == "POST":
            categoria.nome = request.form.get("nome")
            categoria.desc = request.form.get("desc")
            db.session.add(categoria)
            db.session.commit()
            return redirect(url_for("categoria"))
        return render_template("cat_editar.html", categoria = categoria, titulo="Editar Categoria")
    else:
        return redirect(url_for("index"))

@app.route("/categoria/deletar/<int:id>")
@login_required
def deletarcategoria(id):
    if current_user.id == 1:
        categoria = Categoria.query.get(id)
        db.session.delete(categoria)
        db.session.commit()
        return redirect(url_for("categoria"))
    else:
        return redirect(url_for("index"))

@app.route("/cad/usuario/")
def usuario():
    loginMenu()
    return render_template("usuario.html", usuarios = Usuario.query.all(), titulo="Cadastro de Usuário")

@app.route("/usuario/criar", methods=["POST"])
def criarusuario():
    hash = hashlib.sha512(str(request.form.get("passwd")).encode("utf-8")).hexdigest()
    usuario = Usuario(request.form.get("user"), request.form.get("email"), hash, request.form.get("end"), request.form.get("telefone"))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for("usuario"))

@app.route("/usuario/detalhar/<int:id>")
@login_required
def buscarusuario(id):
    valida = validaLogin(id)
    if valida == True:
        return render_template("user_detalhes.html", usuarios = Usuario.query.get(id))
    else:
        return redirect(url_for("index"))

@app.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editarusuario(id):
    valida = validaLogin(id)
    usuario = Usuario.query.get(id)
    if valida == True:
        if request.method == "POST":
            usuario.nome = request.form.get("user")
            usuario.email = request.form.get("email")
            usuario.senha = hashlib.sha512(str(request.form.get("passwd")).encode("utf-8")).hexdigest()
            usuario.end = request.form.get("end")
            usuario.telefone = request.form.get("telefone")
            db.session.add(usuario)
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("user_editar.html", usuario = usuario)
    else:
        return redirect(url_for("index"))

@app.route("/usuario/deletar/<int:id>")
@login_required
def deletarusuario(id):
    valida = validaLogin(id)
    if valida == True:
        usuario = Usuario.query.get(id)
        db.session.delete(usuario)
        db.session.commit()
        return redirect(url_for("usuario")) 
    else:
        return redirect(url_for("index"))

@app.route("/cad/anuncio/")
@login_required
def anuncio():
    categorias = db.session.query(Categoria).all()
    anuncios = db.session.query(Anuncio, Categoria, Usuario).select_from(Anuncio).join(Categoria).join(Usuario).order_by(Anuncio.id).all()
    return render_template("anuncio.html", anuncios = anuncios, categorias = categorias, titulo="Cadastro de Anúncio")

@app.route("/anuncio/meusanuncios")
@login_required
def meusanuncios():
    anuncios = db.session.query(Anuncio, Categoria, Usuario).select_from(Anuncio).join(Categoria).join(Usuario).order_by(Anuncio.id).all()
    return render_template("meusanuncios.html", anuncios = anuncios, titulo="Meus anúncios")

@app.route("/anuncio/criar", methods=["POST"])
@login_required
def criaranuncio():
    anuncio = Anuncio(request.form.get("nome"), request.form.get("desc"),request.form.get("qtd"),request.form.get("preco"), current_user.id, request.form.get("cat"))
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for("anuncio"))

@app.route("/anuncio/detalhar/<int:id>")
@login_required
def buscaranuncio(id):
    anuncios = Anuncio.query.get(id)
    valida = validaLogin(anuncios.idusuario)
    if valida == True:
        return render_template("anunc_detalhes.html", anuncios = anuncios, usuarios= Usuario.query.all(), categorias = Categoria.query.all())
    else:
        return redirect(url_for("index"))

@app.route("/anuncio/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editaranuncio(id):
    anuncio = Anuncio.query.get(id)
    valida = validaLogin(anuncio.idusuario)
    if valida == True:
        if request.method == "POST":
            anuncio.nome = request.form.get("nome")
            anuncio.desc = request.form.get("desc")
            anuncio.qtd = request.form.get("qtd")
            anuncio.preco = request.form.get("preco")
            anuncio.idusuario = current_user.id
            anuncio.idcategoria = request.form.get("cat")
            db.session.add(anuncio)
            db.session.commit()
            return redirect(url_for("anuncio"))
        return render_template("anunc_editar.html", anuncio = anuncio, usuarios= Usuario.query.all(), categorias = Categoria.query.all())
    else:
        return redirect(url_for("index"))

@app.route("/anuncio/deletar/<int:id>")
@login_required
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    valida = validaLogin(anuncio.idusuario)
    if valida == True:
        db.session.delete(anuncio)
        db.session.commit()
        return redirect(url_for("anuncio")) 
    else:
        return redirect(url_for("index"))

@app.route("/anunc/pergunta/")
@login_required
def pergunta():
    perguntas = db.session.query(Pergunta, Anuncio, Usuario).select_from(Pergunta).join(Anuncio).join(Usuario, Pergunta.idusuario == Usuario.id).order_by(Pergunta.id).all()
    respostas = db.session.query(Pergunta, Anuncio, Usuario).select_from(Pergunta).join(Anuncio).join(Usuario).order_by(Pergunta.id).all()
    return render_template("pergunta.html", perguntas = perguntas, respostas = respostas)

@app.route("/pergunta/editar/<int:id>", methods=["GET", "POST"])
def editarperguntas(id):
    if current_user.id == 1:
        pergunta = Pergunta.query.get(id) 
        if request.method == "POST":
            pergunta.pergunta = request.form.get("pergunta")
            pergunta.resposta = request.form.get("resposta")
            pergunta.idusuario = pergunta.idusuario
            pergunta.idanuncio = pergunta.idanuncio
            db.session.add(pergunta)
            db.session.commit()
            return redirect(url_for("pergunta"))
        return render_template("editarpergunta.html", pergunta = pergunta)
    else:
        return redirect(url_for("index"))

@app.route("/pergunta/deletar/<int:id>")
@login_required
def deletarpergunta(id):
    if current_user.id == 1:
        pergunta = Pergunta.query.get(id)
        db.session.delete(pergunta)
        db.session.commit()
        return redirect(url_for("pergunta"))
    else:
        return redirect(url_for("index"))

@app.route("/anunc/fazerpergunta/<int:id>")
@login_required
def fazerpergunta(id):
    anuncio = Anuncio.query.get(id)
    return render_template("fazerpergunta.html", anuncio = anuncio, usuarios= Usuario.query.all())

@app.route("/anunc/pergunta/criar/<int:id>", methods=["POST"])
@login_required
def criarpergunta(id):
    anuncio = Anuncio.query.get(id)
    pergunta = Pergunta(request.form.get("pergunta"), "", current_user.id, anuncio.id)
    db.session.add(pergunta)
    db.session.commit()
    return redirect(url_for("pergunta"))


@app.route("/anunc/pergunta/resposta/<int:id>", methods=["GET","POST"])
@login_required
def editarperguntar(id):
    pergunta = Pergunta.query.get(id) 
    if request.method == "POST":
        pergunta.pergunta = pergunta.pergunta
        pergunta.resposta = request.form.get("resposta")
        pergunta.idusuario = pergunta.idusuario
        pergunta.idanuncio = pergunta.idanuncio
        db.session.add(pergunta)
        db.session.commit()
        return redirect(url_for("pergunta"))
    return render_template("responderpergunta.html", pergunta = pergunta)

@app.route("/anunc/comprar/<int:id>")
@login_required
def comprar(id):
    anuncio = Anuncio.query.get(id)
    aux = anuncio.qtd
    return render_template("comprar.html",aux = aux, anuncio = anuncio, usuarios= Usuario.query.all())

@app.route("/anunc/compra/confirmarcompra/<int:id>", methods=["GET", "POST"])
@login_required
def confirmarcompra(id):
    anuncio = Anuncio.query.get(id)
    if int(request.form.get("qtd")) > anuncio.qtd:
        return render_template("errocompra.html")
    else:
        compra = Compra(anuncio.preco, request.form.get("qtd"), anuncio.preco * float(request.form.get("qtd")), anuncio.id, current_user.id)
        anuncio.nome = anuncio.nome
        anuncio.desc = anuncio.desc
        anuncio.qtd = anuncio.qtd - int(request.form.get("qtd"))
        anuncio.preco = anuncio.preco
        anuncio.idusuario = anuncio.idusuario
        anuncio.idcategoria = anuncio.idcategoria
        db.session.add(compra)
        db.session.commit()
        db.session.add(anuncio)
        db.session.commit()
        return redirect(url_for("index"))

@app.route("/anunc/favoritos/")
@login_required
def favoritos():
    favoritos = db.session.query(Favorito, Anuncio, Usuario).select_from(Favorito).join(Anuncio).join(Usuario, Favorito.idusuario == Usuario.id).order_by(Favorito.id).all()
    return render_template("favoritos.html", favoritos = favoritos)

@app.route("/favoritos/criar/<int:id>", methods=["GET","POST"])
@login_required
def criarfavoritos(id):
    anuncio = Anuncio.query.get(id)
    favorito = Favorito(anuncio.id, current_user.id)
    db.session.add(favorito)
    db.session.commit()
    return redirect(url_for("favoritos"))

@app.route("/favoritos/detalhar/<int:id>")
@login_required
def detalhesfavoritos(id):
    anuncio = Anuncio.query.get(id)
    return render_template("detalhesfavoritos.html", anuncio = anuncio)

@app.route("/favoritos/deletar/<int:id>")
@login_required
def deletarfavoritos(id):
    favorito = Favorito.query.get(id)
    if current_user.id == favorito.idusuario:
        if favorito: 
            db.session.delete(favorito)
            db.session.commit()
            return redirect(url_for("favoritos")) 
    elif current_user.id == 1:
        if favorito: 
            db.session.delete(favorito)
            db.session.commit()
            return redirect(url_for("favoritos")) 
    else:
        return redirect(url_for("index"))

@app.route("/rel/vendas")
@login_required
def relVendas():
    vendas = db.session.query(Compra, Anuncio, Usuario).select_from(Compra).join(Anuncio).join(Usuario).order_by(Compra.id).all()
    return render_template("relVendas.html", vendas = vendas)

@app.route("/rel/compras")
@login_required
def relCompras():
    compras = db.session.query(Compra, Anuncio, Usuario).select_from(Compra).join(Anuncio).join(Usuario, Compra.idusuario == Usuario.id).order_by(Compra.id).all()
    return render_template("relCompras.html", compras = compras)

@app.route("/adm/")
@login_required
def adm():
    if current_user.id == 1:
        usuarios = db.session.query(Usuario).order_by(Usuario.id).all()
        anuncios = db.session.query(Anuncio, Categoria, Usuario).select_from(Anuncio).join(Categoria).join(Usuario).order_by(Anuncio.id).all()
        categorias = db.session.query(Categoria).order_by(Categoria.id).all()
        perguntas = db.session.query(Pergunta, Anuncio, Usuario).select_from(Pergunta).join(Anuncio).join(Usuario, Pergunta.idusuario == Usuario.id).order_by(Pergunta.id).all()
        respostas = db.session.query(Pergunta, Anuncio, Usuario).select_from(Pergunta).join(Anuncio).join(Usuario).order_by(Pergunta.id).all()
        favoritos = db.session.query(Favorito, Anuncio, Usuario).select_from(Favorito).join(Anuncio).join(Usuario, Favorito.idusuario == Usuario.id).order_by(Favorito.id).all()
        compras = db.session.query(Compra, Anuncio, Usuario).select_from(Compra).join(Anuncio).join(Usuario, Compra.idusuario == Usuario.id).order_by(Compra.id).all()
        vendas = db.session.query(Compra, Anuncio, Usuario).select_from(Compra).join(Anuncio).join(Usuario).order_by(Compra.id).all()
        return render_template("adm.html", usuarios = usuarios, anuncios = anuncios, categorias = categorias, perguntas = perguntas, respostas = respostas, favoritos = favoritos, compras = compras, vendas = vendas)
    else:
        return redirect(url_for("index"))

if __name__ == "sonegocio":
	db.create_all()

