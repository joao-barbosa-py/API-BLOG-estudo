# Permite criar API
from flask import Flask
# Permite crirar o banco de dados
from flask_sqlalchemy import SQLAlchemy
# Colocar nossas estruturas dentro do arquivos Estruturas banco de dados


# Criar uma API flask
app = Flask(__name__);
# Criar uma instância de SQLAlchemy
    # Definindo informações importante da configuração do BD

# Importante para gerar acesso de Autenticação unico, da sua aplicação
app.config["SECRET_KEY"] = "P@ssAlun0"
# Definir onde está localizado o nosso banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

# Instanciando o SQLAlchemy
db = SQLAlchemy(app)
app.app_context().push()
# Tipando variável como SQLAlchemy
db: SQLAlchemy

# Definir a estrutura da tabela Postagem
    # Toda postagem deve receber um id de postagem, um titulo e um autor
class Postagem(db.Model):
    __tablename__ = "postagem"
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    #Autor
    id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))

# Definir a estrutura da tabela Autor 
    # id_autor, nome, email, senha, admin, histórico de postagens
class Autor(db.Model):
    __tablename__ = "autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship("Postagem")



def inicializar_banco():
    # Executar o comando para criar o Banco de Dados
    db.drop_all()
    # Criar todas as tabelas associadas ao db
    db.create_all()

    # Criando usuários administradores
    autor = Autor(nome="joao", email="joao@gmail.com",senha="12345",admin=True)
    # Adicionando autor ao bando de dados
    db.session.add(autor)
    # Dados só serão salvos quando rodar o comando
    db.session.commit()

# Caso contrario a função não sera chamada e o banco não ficará sendo apagado
if __name__ == "__main__":
    inicializar_banco()