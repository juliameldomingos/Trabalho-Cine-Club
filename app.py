# Importamos do Flask apenas o que o projeto precisa:
#   Flask           -> cria a aplicação
#   render_template -> mostra um arquivo HTML da pasta "templates"
#   request         -> lê os dados enviados pelos formulários
#   redirect        -> manda o navegador para outra rota (endereço)
#   url_for         -> gera o endereço de uma rota a partir do nome da função
#   session         -> "memória" do navegador: guarda quem está logado
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'cine-club-chave-secreta'   # necessária para usar o session

# -----------------------------------------------------------------
# Dados provisórios: listas de dicionários guardadas na memória.
# Quando o servidor reinicia, os dados voltam ao que está aqui.
# (Na Aula 05, com o MySQL, elas viram tabelas de verdade.)
# -----------------------------------------------------------------
usuarios = [
    {'id': 1, 'nome': 'Ana Souza', 'email': 'admin@cineclub.com', 'celular': '(14) 99999-0001',
     'nascimento': '1995-04-12', 'cpf': '123.456.789-00', 'nivel': 'Administrador',
     'cep': '17201-000', 'endereco': 'Rua Paissandu', 'numero': '100',
     'complemento': '', 'cidade': 'Jaú', 'estado': 'SP', 'senha': '123456'},
    {'id': 2, 'nome': 'Carlos Lima', 'email': 'carlos@example.com', 'celular': '(14) 99999-0002',
     'nascimento': '1990-09-30', 'cpf': '987.654.321-00', 'nivel': 'Usuário',
     'cep': '17201-100', 'endereco': 'Av. Brasil', 'numero': '250',
     'complemento': 'Apto 4', 'cidade': 'Jaú', 'estado': 'SP', 'senha': '123456'}
]

filmes = [
    {'id': 1, 'titulo': 'O Poderoso Chefão', 'diretor': 'Francis Ford Coppola',
     'genero': 'Crime', 'ano': '1972'},
    {'id': 2, 'titulo': 'Matrix', 'diretor': 'Lana e Lilly Wachowski',
     'genero': 'Ficção científica', 'ano': '1999'},
    {'id': 3, 'titulo': 'Procurando Nemo', 'diretor': 'Andrew Stanton',
     'genero': 'Infantil', 'ano': '2003'},
    {'id': 4, 'titulo': 'Harry Potter e a Pedra Filosofal', 'diretor': 'Chris Columbus',
     'genero': 'Fantasia', 'ano': '2001'}
]

sessoes = [
    {'id': 1, 'filme': 'O Poderoso Chefão', 'data': '24/10/2026', 'horario': '14:00',
     'sala': 'Sala 1 - Standard', 'valor': '25,00'},
    {'id': 1, 'filme': 'O Poderoso Chefão', 'data': '24/10/2026', 'horario': '19:00',
     'sala': 'Sala 2 - IMAX', 'valor': '25,00'},
    {'id': 2, 'filme': 'Matrix', 'data': '25/10/2026', 'horario': '19:00',
     'sala': 'Sala 1 - Standard', 'valor': '25,00'},
    {'id': 3, 'filme': 'O Poderoso Chefão', 'data': '24/10/2026', 'horario': '14:00',
     'sala': 'Sala 2 - IMAX', 'valor': '25,00'},
    {'id': 4, 'filme': 'Harry Potter e a Pedra Filosofal', 'data': '24/10/2026', 'horario': '19:30',
          'sala': 'Sala 3 - VIP', 'valor': '30,00'}
]

# Opções que aparecem nos campos de seleção (<select>)
NIVEIS = ['Usuário', 'Administrador']
ESTADOS = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA',
           'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
GENEROS = ['Ação', 'Animação', 'Aventura', 'Comédia', 'Crime', 'Drama', 'Fantasia', 'Ficção científica', 'Intantil', 'Terror', 'Romance']
SALAS = ['Sala 1 - Standard', 'Sala 2 - IMAX', 'Sala 3 - VIP']


# Devolve o próximo número de ID: o maior ID da lista + 1.
# (Não dá para usar len(lista) + 1, porque depois de excluir um item o número se repetiria.)
def proximo_id(lista):
    maior = 0
    for item in lista:
        if item['id'] > maior:
            maior = item['id']
    return maior + 1


# Procura na lista o item com o ID informado. Devolve o item, ou None se não existir.
def buscar(lista, id):
    for item in lista:
        if item['id'] == id:
            return item
    return None


# -----------------------------------------------------------------
# Controle de acesso
#   - Quem não fez login volta para a tela de login.
#   - A aba USUÁRIOS (listagem e cadastro) é só do Administrador.
#   - Os CADASTROS de filmes e sessões também são só do Administrador.
#   - Usuário comum só consulta o dashboard e as listagens de filmes e sessões.
# A função devolve uma resposta quando o acesso é negado e None quando é permitido.
# -----------------------------------------------------------------
def verificar_acesso(somente_admin=False):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if somente_admin and session.get('nivel') != 'Administrador':
        return render_template('acesso_negado.html'), 403
    return None


# =================================================================
# PÁGINAS SEM MENU (template base_login.html)
# =================================================================
@app.route('/', methods=['GET', 'POST'])
def login():
    """Tela de login. GET mostra o formulário; POST confere e-mail e senha."""
    erros = []

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()

        # Procura na lista um usuário com esse e-mail e essa senha
        encontrado = None
        for u in usuarios:
            if u['email'].lower() == email and u['senha'] == senha:
                encontrado = u

        if encontrado is not None:
            session['usuario'] = encontrado['nome']   # guarda quem entrou
            session['nivel'] = encontrado['nivel']    # 'Usuário' ou 'Administrador'
            session['email'] = encontrado['email']    # usado para impedir que alguém exclua a si mesmo
            return redirect(url_for('dashboard'))   # vai para o dashboard
        erros.append('E-mail ou senha incorretos.')

    return render_template('login.html', erros=erros, sucesso=None)


@app.route('/cadastrar', methods=['GET', 'POST'])
def registrar():
    """Botão CADASTRAR do login: o próprio usuário cria sua conta."""
    erros = []
    dados_form = {'nome': '', 'email': ''}

    if request.method == 'POST':
        dados_form['nome'] = request.form.get('nome', '').strip()
        dados_form['email'] = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        confirmar = request.form.get('confirmar', '').strip()

        if not dados_form['nome'] or not dados_form['email'] or not senha:
            erros.append('Preencha o nome, o e-mail e a senha.')
        elif len(senha) < 6:
            erros.append('A senha deve ter pelo menos 6 caracteres.')
        elif senha != confirmar:
            erros.append('As senhas não conferem.')

        # Não permite dois usuários com o mesmo e-mail
        for u in usuarios:
            if u['email'].lower() == dados_form['email'].lower():
                erros.append('Este e-mail já está cadastrado.')

        if not erros:
            novo = {'id': proximo_id(usuarios), 'nome': dados_form['nome'],
                    'email': dados_form['email'], 'celular': '', 'nascimento': '',
                    'cpf': '', 'nivel': 'Usuário', 'cep': '', 'endereco': '',
                    'numero': '', 'complemento': '', 'cidade': '', 'estado': '',
                    'senha': senha}
            usuarios.append(novo)
            return render_template('login.html', erros=[],
                                   sucesso='Conta criada com sucesso! Faça login.')

    return render_template('registrar.html', erros=erros, dados_form=dados_form)


@app.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    """Link Recuperar Senha: define uma nova senha para o e-mail informado."""
    erros = []

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        confirmar = request.form.get('confirmar', '').strip()

        usuario = None
        for u in usuarios:
            if u['email'].lower() == email:
                usuario = u

        if usuario is None:
            erros.append('Não existe usuário com este e-mail.')
        elif len(senha) < 6:
            erros.append('A nova senha deve ter pelo menos 6 caracteres.')
        elif senha != confirmar:
            erros.append('As senhas não conferem.')
        else:
            usuario['senha'] = senha
            return render_template('login.html', erros=[],
                                   sucesso='Senha alterada! Entre com a nova senha.')

    return render_template('recuperar_senha.html', erros=erros)


@app.route('/sair')
def sair():
    session.clear()                      # esquece quem estava logado
    return redirect(url_for('login'))


# =================================================================
# PÁGINAS COM MENU (template base.html)
# =================================================================
@app.route('/dashboard')
def dashboard():
    bloqueio = verificar_acesso()
    if bloqueio is not None:
        return bloqueio
    return render_template('dashboard.html')


# ------------------------- USUÁRIOS -------------------------
@app.route('/usuarios')
def listar_usuarios():
    bloqueio = verificar_acesso(somente_admin=True)   # só Administrador
    if bloqueio is not None:
        return bloqueio
    return render_template('listar_usuarios.html', usuarios=usuarios)


# Esta função atende DUAS rotas:
#   /usuarios/cadastrar        -> id vale None  (cadastro de um novo usuário)
#   /usuarios/editar/<id>      -> id vem da URL (edição de um usuário existente)
@app.route('/usuarios/cadastrar', methods=['GET', 'POST'])
@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def cadastrar_usuario(id=None):
    bloqueio = verificar_acesso(somente_admin=True)   # só Administrador
    if bloqueio is not None:
        return bloqueio

    # Na edição, procuramos o usuário na lista; se não existir, volta para a listagem
    usuario = None
    if id is not None:
        usuario = buscar(usuarios, id)
        if usuario is None:
            return redirect(url_for('listar_usuarios'))

    erros = []
    sucesso = None
    campos = ['nome', 'email', 'celular', 'nascimento', 'cpf', 'nivel',
              'cep', 'endereco', 'numero', 'complemento', 'cidade', 'estado']

    # dados_form guarda o que aparece nos campos. Na edição começa com os dados do usuário.
    dados_form = {}
    for campo in campos:
        if usuario is not None:
            dados_form[campo] = usuario[campo]
        else:
            dados_form[campo] = ''

    if request.method == 'POST':
        for campo in campos:
            dados_form[campo] = request.form.get(campo, '').strip()

        # Validação
        if not dados_form['nome']:
            erros.append('Informe o nome.')
        if not dados_form['email']:
            erros.append('Informe o e-mail.')
        else:
            for u in usuarios:
                # "u is not usuario" evita acusar o e-mail do próprio usuário que está sendo editado
                if u['email'].lower() == dados_form['email'].lower() and u is not usuario:
                    erros.append('Já existe um usuário com este e-mail.')
        if not dados_form['nivel']:
            erros.append('Escolha o nível de acesso.')

        # Se não houve erros, salva
        if not erros:
            if usuario is not None:
                # EDIÇÃO: atualiza os campos do usuário que já existe (a senha não é mexida)
                for campo in campos:
                    usuario[campo] = dados_form[campo]
                return redirect(url_for('listar_usuarios'))

            # CADASTRO: cria um novo usuário
            novo = dados_form.copy()          # copia o dicionário
            novo['id'] = proximo_id(usuarios)
            novo['senha'] = ''                # a senha é definida em "Recuperar Senha"
            usuarios.append(novo)
            sucesso = 'Usuário cadastrado com sucesso!'
            for campo in campos:              # limpa o formulário
                dados_form[campo] = ''

    return render_template('cadastrar_usuario.html', erros=erros, sucesso=sucesso,
                           dados_form=dados_form, editando=usuario is not None,
                           niveis=NIVEIS, estados=ESTADOS)


@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
def excluir_usuario(id):
    bloqueio = verificar_acesso(somente_admin=True)
    if bloqueio is not None:
        return bloqueio

    usuario = buscar(usuarios, id)
    # Ninguém pode excluir a própria conta (senão poderia ficar sem administrador)
    if usuario is not None and usuario['email'] != session.get('email'):
        usuarios.remove(usuario)
    return redirect(url_for('listar_usuarios'))


# -------------------------- FILMES --------------------------
@app.route('/filmes')
def listar_filmes():
    bloqueio = verificar_acesso()
    if bloqueio is not None:
        return bloqueio
    return render_template('listar_filmes.html', filmes=filmes)


@app.route('/filmes/cadastrar', methods=['GET', 'POST'])
@app.route('/filmes/editar/<int:id>', methods=['GET', 'POST'])
def cadastrar_filme(id=None):
    bloqueio = verificar_acesso(somente_admin=True)   # só Administrador
    if bloqueio is not None:
        return bloqueio

    filme = None
    if id is not None:
        filme = buscar(filmes, id)
        if filme is None:
            return redirect(url_for('listar_filmes'))

    erros = []
    sucesso = None
    campos = ['titulo', 'diretor', 'genero', 'ano']
    dados_form = {}
    for campo in campos:
        if filme is not None:
            dados_form[campo] = filme[campo]
        else:
            dados_form[campo] = ''

    if request.method == 'POST':
        for campo in campos:
            dados_form[campo] = request.form.get(campo, '').strip()

        if not dados_form['titulo']:
            erros.append('Informe o título do filme.')
        if not dados_form['diretor']:
            erros.append('Informe o diretor.')
        if not dados_form['genero']:
            erros.append('Escolha o gênero.')
        if not dados_form['ano']:
            erros.append('Informe o ano de lançamento.')
        else:
            try:
                ano = int(dados_form['ano'])
                if ano < 1888 or ano > 2100:
                    erros.append('O ano deve estar entre 1888 e 2100.')
            except ValueError:
                erros.append('O ano deve ser um número inteiro.')

        if not erros:
            if filme is not None:
                # EDIÇÃO: se o título mudou, as sessões desse filme acompanham o novo título
                for s in sessoes:
                    if s['filme'] == filme['titulo']:
                        s['filme'] = dados_form['titulo']
                for campo in campos:
                    filme[campo] = dados_form[campo]
                return redirect(url_for('listar_filmes'))

            novo = dados_form.copy()
            novo['id'] = proximo_id(filmes)
            filmes.append(novo)
            sucesso = 'Filme cadastrado com sucesso!'
            for campo in campos:
                dados_form[campo] = ''

    return render_template('cadastrar_filme.html', erros=erros, sucesso=sucesso,
                           dados_form=dados_form, editando=filme is not None,
                           generos=GENEROS)


@app.route('/filmes/excluir/<int:id>', methods=['POST'])
def excluir_filme(id):
    bloqueio = verificar_acesso(somente_admin=True)
    if bloqueio is not None:
        return bloqueio

    filme = buscar(filmes, id)
    if filme is None:
        return redirect(url_for('listar_filmes'))

    # Não deixa excluir um filme que ainda tem sessões marcadas.
    for s in sessoes:
        if s['filme'] == filme['titulo']:
            return render_template('listar_filmes.html', filmes=filmes,
                                   erros=['Não é possível excluir "' + filme['titulo'] +
                                          '": existem sessões cadastradas para ele. Exclua as sessões primeiro.'])

    filmes.remove(filme)
    return redirect(url_for('listar_filmes'))


# ------------------------- SESSÕES --------------------------
@app.route('/sessoes')
def listar_sessoes():
    bloqueio = verificar_acesso()
    if bloqueio is not None:
        return bloqueio
    return render_template('listar_sessoes.html', sessoes=sessoes)


@app.route('/sessoes/cadastrar', methods=['GET', 'POST'])
@app.route('/sessoes/editar/<int:id>', methods=['GET', 'POST'])
def cadastrar_sessao(id=None):
    bloqueio = verificar_acesso(somente_admin=True)   # só Administrador
    if bloqueio is not None:
        return bloqueio

    sessao = None
    if id is not None:
        sessao = buscar(sessoes, id)
        if sessao is None:
            return redirect(url_for('listar_sessoes'))

    erros = []
    sucesso = None
    campos = ['filme', 'sala', 'data', 'horario', 'valor']
    dados_form = {}
    for campo in campos:
        if sessao is not None:
            dados_form[campo] = sessao[campo]
        else:
            dados_form[campo] = ''

    # Na edição, a data guardada é 25/10/2026, mas o campo de data do HTML precisa de 2026-10-25
    if sessao is not None:
        partes = sessao['data'].split('/')
        dados_form['data'] = partes[2] + '-' + partes[1] + '-' + partes[0]

    # Lista com os títulos dos filmes cadastrados (para o <select> do formulário)
    titulos = []
    for f in filmes:
        titulos.append(f['titulo'])

    if request.method == 'POST':
        for campo in campos:
            dados_form[campo] = request.form.get(campo, '').strip()

        if dados_form['filme'] not in titulos:
            erros.append('Escolha um filme da lista.')
        if not dados_form['sala']:
            erros.append('Escolha a sala.')
        if not dados_form['data']:
            erros.append('Informe a data da sessão.')
        if not dados_form['horario']:
            erros.append('Informe o horário da sessão.')
        try:
            valor = float(dados_form['valor'].replace(',', '.'))
            if valor < 0:
                erros.append('O valor do ingresso não pode ser negativo.')
        except ValueError:
            erros.append('O valor do ingresso deve ser um número (ex.: 25,00).')

        if not erros:
            novo = dados_form.copy()
            # O campo de data envia 2026-10-25; guardamos como 25/10/2026
            partes = novo['data'].split('-')
            novo['data'] = partes[2] + '/' + partes[1] + '/' + partes[0]
            novo['valor'] = '{:.2f}'.format(valor).replace('.', ',')

            if sessao is not None:
                # EDIÇÃO
                for campo in campos:
                    sessao[campo] = novo[campo]
                return redirect(url_for('listar_sessoes'))

            # CADASTRO
            novo['id'] = proximo_id(sessoes)
            sessoes.append(novo)
            sucesso = 'Sessão cadastrada com sucesso!'
            for campo in campos:
                dados_form[campo] = ''

    return render_template('cadastrar_sessao.html', erros=erros, sucesso=sucesso,
                           dados_form=dados_form, editando=sessao is not None,
                           filmes=titulos, salas=SALAS)


@app.route('/sessoes/excluir/<int:id>', methods=['POST'])
def excluir_sessao(id):
    bloqueio = verificar_acesso(somente_admin=True)
    if bloqueio is not None:
        return bloqueio

    sessao = buscar(sessoes, id)
    if sessao is not None:
        sessoes.remove(sessao)
    return redirect(url_for('listar_sessoes'))


if __name__ == '__main__':
    app.run(debug=True)
