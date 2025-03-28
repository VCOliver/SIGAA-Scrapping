# SIGAAMOS Bot

Este projeto é um bot do Telegram para gerenciar notificações do SIGAA. O bot permite que os usuários recebam avisos sobre a disponibilidade de matérias na matrícula extraordinária.

## Funcionalidades

- **/start**: Inicia uma conversa com o bot.
- **/search**: Pesquisa por uma matéria específica.
- **/warn**: Configura um aviso para quando uma matéria estiver disponível.

## Estrutura do Projeto

- `Telegram/telegram_bot.py`: Contém a classe `SIGAAMOS_bot` que gerencia a interação com o Telegram.
- `Database/database.py`: Contém a classe `Database` que gerencia a interação com o banco de dados SQLite.
- `Scrapping/main.py`: Ponto de entrada principal para a aplicação do bot.
- `install_geckodriver.sh`: Script para instalação rápida do GeckoDriver (Raspberry Pi)

## Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/sigaamos-bot.git
    cd sigaamos-bot
    ```

2. Crie um ambiente virtual e ative-o:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4. Crie um arquivo `.env` na raiz do projeto e adicione o token do seu bot do Telegram:
    ```env
    BOT_TOKEN=seu_token_do_telegram
    ```

5. Installe o GeckoDriver:
	```bash
	sudo bash install_geckodriver.sh
	```

## Uso

1. Inicie o bot:
    ```bash
    python Scrapping/main.py
    ```

2. No Telegram, inicie uma conversa com o bot e use os comandos disponíveis:
    - `/start`: Inicia a conversa com o bot.
    - `/search <matéria>`: Pesquisa por uma matéria específica.
    - `/warn <matéria>`: Configura um aviso para quando a matéria estiver disponível.
	- `/warn stop <matéria>`: Remove o aviso da matéria

