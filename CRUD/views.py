from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from CRUD.models import Usuario
from CRUD.forms import CadastroForm, LoginForm, EditarForm
from CRUD import app, db
import logging
import time

# Controle de tentativas de login
tentativas_login = {}

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        novo_usuario = Usuario(nome=form.nome.data, email=form.email.data)
        novo_usuario.set_senha(form.senha.data)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Conta criada com sucesso! Faça login.', 'success')
        logging.info(f"Usuário cadastrado: {novo_usuario.email} em {time.strftime('%Y-%m-%d %H:%M:%S')}")
        return redirect(url_for('login'))
    return render_template('cadastro.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        email = form.email.data
        senha = form.senha.data

        # Verificar tentativas
        tentativas = tentativas_login.get(email, 0)
        if tentativas >= 5:
            flash('Muitas tentativas de login. Tente novamente mais tarde.', 'danger')
            return redirect(url_for('login'))

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            tentativas_login[email] = 0  # resetar tentativas
            flash('Login efetuado com sucesso!', 'success')
            logging.info(f"Login realizado: {usuario.email} em {time.strftime('%Y-%m-%d %H:%M:%S')}")
            return redirect(url_for('index'))
        else:
            tentativas_login[email] = tentativas + 1
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logging.info(f"Logout realizado: {current_user.email} em {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logout_user()
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/perfil/<int:id>', methods=['GET', 'POST'])
@login_required
def perfil(id):
    usuario = Usuario.query.get_or_404(id)
    if usuario.id != current_user.id:
        flash('Você não tem permissão para alterar este perfil.', 'danger')
        return redirect(url_for('index'))
    form = EditarForm(obj=usuario)
    
    if form.validate_on_submit():
        logging.info(f"Perfil atualizado: {current_user.email} em {time.strftime('%Y-%m-%d %H:%M:%S')}")
        form.populate_obj(usuario)
        if form.senha.data:
            usuario.set_senha(form.senha.data)
        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for('perfil', id=usuario.id))
        
    return render_template('perfil.html', usuario=current_user, form=form)

@app.route('/deletar_perfil/<int:id>', methods=['POST'])
@login_required
def deletar_perfil(id):
    usuario = Usuario.query.get_or_404(id)
    if usuario.id != current_user.id:
        flash('Você não tem permissão para deletar este perfil.', 'danger')
        return redirect(url_for('perfil', id=id))
    else:
        db.session.delete(usuario)
        db.session.commit()
        flash('Perfil deletado com sucesso.', "success")
        logging.info(f"Perfil deletado: id: {current_user.id}. E-mail: {current_user.email} em {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    logout_user()
    return redirect(url_for('login'))