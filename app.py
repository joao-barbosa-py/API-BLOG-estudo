##FLASK
from flask import jsonify, request, make_response
# Colocar nossas estruturas dentro de esturas banco de dados para este arquivo
from estrutura_banco_de_dados1 import Autor, Postagem, app, db
import jwt
from datetime import datetime, timedelta
import json
from functools import wraps


# Reutilizar essa autenticação de token em qualquer requisição 
def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificando se o arquivo token foi enviado
        if "x-access-token" in request.headers:
            request.headers["x-access-token"]
        if not token:
            return jsonify({"mensagem": "Token não foi incluído!"}, 401)
        # Caso exista o token, decodificar o token e validar acesso consultando o BD
        try:
            resultado = jwt.decode(token,app.config["SECRET_KEY"])
            # Verificando se essas informações estão cadastrada no nosso BD
            autor = Autor.query.filter_by(id_autor=resultado["id_autor"]).first()
        except:
            return jsonify({"Mensagem":"Token é inválido"},401)
        return f(autor,*args,**kwargs)
    return decorated

# API DE UM BLOG

@app.route("/login")
def login():
    # Estrair informações de autenticação que foram passadas pra esse API
    auth  = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response("Login inválido", 401, {"WWW-Authenticate":"Basic realm='login Obrigatório'"})
    # Verificando se temos um usuário e se ele é válido
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response("Login inválido", 401, {"WWW-Authenticate":"Basic realm='login Obrigatório'"})
    # Verificando se a senha passada está correta ou não 
    if auth.password == usuario.senha:
        # A senha estando correta nós retornamos um token para o usuário
        token = jwt.encode({"id_autor":usuario.id_autor,"exp":datetime.utcnow() + timedelta(minutes= 30)}, app.config["SECRET_KEY"])
        # Retornando informação e decodificando ela para ficar legível para os usuários
        return jsonify({"token": token})
    return make_response("Login inválido", 401, {"WWW-Authenticate":"Basic realm='login Obrigatório'"})


@app.route("/")
@token_obrigatorio
def obter_postagens(autor, autor_atual):
    postagens = Postagem.query.all()
    lista_de_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual["titulo"] = postagem.titulo
        postagem_atual["id_autor"] = postagem.id_autor
        
        # Adicionando o novo autor a lista de autores
        lista_de_postagens.append(postagem_atual)
    
    return jsonify({"postagens" : lista_de_postagens})

# ROTA - GET com id http://localhost:5000/postagens/1
@app.route("/postagens/<int:id_postagem>",methods=["GET"])
@token_obrigatorio
def obter_postagem_por_id(autor, id_postagem):
    # Pegar nome da tabéla postagem 
    postagem = Postagem.query.filter_by(autor_atual = id_postagem).first()

    postagem_atual = {}
    postagem_atual["titulo"] = postagem.titulo
    postagem_atual["id_autor"] = postagem.id_autor

    # Obter no formato Json
    return jsonify({"postagem" :postagem_atual})

#Criar nova postagem - POST
@app.route("/postagens", methods=["POST"])
@token_obrigatorio
def nova_postagem(autor, autor_atual):

    # Obter informações que estão chegando para mim
    novo_postagem = request.get_json()
    postagem = Postagem(titulo=postagem["titulo"],id_autor=postagem["id_autor"])

    # salvando usuário no Banco de dados
    db.session.add(nova_postagem)
    db.session.commit()

    return jsonify({"nova postagem":"Postagem criada com sucesso"},200)

# Alterar uma postagem existente - PUT
@app.route("/postagem/<int:id_postagem>", methods=["PUT"])
@token_obrigatorio
def alterar_postagem(autor , autor_atual, id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    
    postagem.titulo = postagem_alterada["titulo"]
    postagem.id_autor = postagem_alterada["id_autor"]

    db.session.commit()
    return jsonify({"mensagem": "Postagem alterada com sucesso!"}, 200)

#Excluir recurso - DELETE
@app.route("/postagem/<int:id_postagem>", methods=["DELETE"])
@token_obrigatorio
def excluir_postagem(autor, autor_atual, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem:
        return jsonify({"mensagem": "A postagem foi excluida"})
    
    db.session.delete(postagem)
    db.session.commit


    return jsonify("Não foi possível encontrar a postagem para exclusão", 404)


# Rota para pegar todos os autores
@app.route("/autores")
@token_obrigatorio
# Criando função que representa isso
def obter_autores(autor):
    #Extraindo todos os dados que tem dentro daquela tabéla
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual["id_autor"] = autor.id_autor
        autor_atual["nome"] = autor.nome
        autor_atual["email"] = autor.email
        
        # Adicionando o novo autor a lista de autores
        lista_de_autores.append(autor_atual)
    
    return jsonify({"autores" : lista_de_autores})

# Rota de obter autores por ID
@app.route("/autores/<int:id_autor>", methods=["GET"])
@token_obrigatorio
# Função para obter autor por id 
def obter_autor_por_id(autor, id_autor):
    # Pegar nome da tabéla autor 
    autor = Autor.query.filter_by(id_autor = id_autor).first()
    if not autor:
        return jsonify(f"Autor não encontrado!")
    autor_atual = {}
    autor_atual["id_autor"] = autor.id_autor
    autor_atual["nome"] = autor.nome
    autor_atual["email"] = autor.email

    # Obter no formato Json
    return jsonify({"autor" :autor_atual})
# Crirar novos autores
@app.route("/autores",methods=["POST"])
@token_obrigatorio
def novo_autor(autor):
    print("Deu merda")
    # Obter informações que estão chegando para mim
    novo_autor = request.get_json()
    autor = Autor(nome=novo_autor["nome"],senha=novo_autor["senha"], email=novo_autor["email"])

    # salvando usuário no Banco de dados
    db.session.add(autor)
    db.session.commit()

    return jsonify({"mensagem":"Usuário criado com sucesso"},200)

# Rota para editar recursos existentes
@app.route("/autores/<int:id_autor>",methods= ["PUT"])
@token_obrigatorio
# Função que recebe e altera o ID do Autor
def alterar_autor(autor, id_autor):
    # Buscar informação do autor 
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    try:
        if not autor:
            return jsonify({"Mensagem": "Este usuário não foi encontrado"})
    except:
        pass
    try:
        if usuario_a_alterar["nome"]:
            autor.nome = usuario_a_alterar["nome"]
    except:
        pass
    try:
        if usuario_a_alterar["email"]:
            autor.email = usuario_a_alterar["email"]
    except:
        pass
    try:
        if usuario_a_alterar["senha"]:
            autor.senha = usuario_a_alterar["senha"]
    except:
        pass
    # Salvando alterações no banco de dados
    db.session.commit()
    return jsonify({"mensagem": "Usuário alterado com sucesso!"})
    
# Rota para excluir um autor
@app.route("/autores/<int:id_autor>", methods=["DELETE"])
@token_obrigatorio
# Função para excluir autor
def excluir_autor(autor, id_autor):
    # Verificar se de fato esse autor existe
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({"mensagem":"Este autor não foi encontrado!"})
    # Caso o autor seja encontrado, estaremos excluindo ele 
    db.session.delete(autor_existente)
    # Salvando as alterções de exclusão
    db.session.commit()

    return jsonify({"mensagem": "Autor excluido com sucesso"})

# Rodar o servidor Flask
app.run(port=5000,host="localhost",debug=True)

