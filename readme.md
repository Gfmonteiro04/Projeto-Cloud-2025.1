# Projeto Cloud Binance

## Descrição
O **Projeto Cloud Binance** é uma aplicação desenvolvida em **Django** para a criação de um **bot de trading** automatizado, focado na compra e venda de criptomoedas na **Binance**. O projeto está hospedado na **Azure**, utilizando diversos serviços em nuvem para garantir escalabilidade, segurança e alta disponibilidade.

## Tecnologias Utilizadas
- **Linguagem**: Python (Django Framework)
- **Banco de Dados**: MySQL (Hospedado na Azure)
- **Infraestrutura**: Azure App Service, API Gateway, e SQL Database
- **Integração**: API da Binance para execução de ordens de compra e venda
- **Automatização**: GitHub Actions para CI/CD

## Funcionalidades
- Cadastro e autenticação de usuários
- Integração com a API da Binance para operações de trading
- Painel de controle para monitoramento das transações
- Logs de transações e histórico de operações
- Hospedagem na Azure para acessibilidade global

## Instalação e Configuração Local
Para rodar o projeto localmente, siga os passos abaixo:

### 1. Clone o repositório
```sh
 git clone https://github.com/seu-usuario/project_cloud_binance.git
 cd project_cloud_binance
```

### 2. Ative o ambiente virtual
```sh
 python -m venv ambiente
 source ambiente/bin/activate  # Linux/Mac
 ambiente\Scripts\activate  # Windows
```

### 3. Instale as dependências
```sh
 pip install -r requirements.txt
```

### 4. Configure o banco de dados
Edite o arquivo **settings.py** para conectar ao MySQL hospedado na Azure:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nome_do_banco',
        'USER': 'usuario',
        'PASSWORD': 'senha',
        'HOST': 'azure_mysql_host',
        'PORT': '3306',
    }
}
```

### 5. Execute as migrações do banco
```sh
 python manage.py migrate
```

### 6. Inicie o servidor
```sh
 python manage.py runserver
```
Acesse no navegador: **http://127.0.0.1:8000/**

## Implantando no Azure
Se quiser fazer o deploy na Azure, utilize os seguintes comandos:
```sh
git add .
git commit -m "Deploy para Azure"
git push azure main
```

Ou use a Azure CLI:
```sh
az webapp up --name projeto-cloud-binance --resource-group ibmec-cloud-2025 --runtime "PYTHON|3.9"
```

## Problemas Conhecidos e Solução
### **Erro 403 - CSRF Verification Failed**
Se você encontrar um erro de **CSRF Verification**, adicione o seguinte no `settings.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    "https://projeto-cloud-binance.azurewebsites.net",
]
```

### **Erro 404 - Recurso não localizado**
- Verifique se o App Service está ativo no Azure Portal
- Confirme se o deploy foi concluído com sucesso
- Reinicie o App Service:  
```sh
az webapp restart --name projeto-cloud-binance --resource-group ibmec-cloud-2025
```

