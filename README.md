# Blaze Double Bot

Este é um bot automatizado para o jogo **Double** no site Blaze. Ele acompanha os resultados recentes da roleta e faz entradas automáticas com base em uma estratégia pré-definida, enviando notificações via Telegram.

## Requisitos

- **Python 3.8+**
- Navegador **Google Chrome**
- **Chromedriver** compatível com a versão do Chrome instalada

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seuusuario/blaze-double-bot.git
cd blaze-double-bot
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Certifique-se de que o arquivo `chromedriver` esteja no PATH ou na mesma pasta do script.

## Configuração

1. Atualize as informações no arquivo `bot_blaze.py`:
   - Substitua o token do Telegram (`token`) com o token do seu bot.
   - Substitua `chat_id` com o ID do chat do Telegram onde as notificações serão enviadas.

2. Execute o script:

```bash
python bot_blaze.py
```

## Funcionamento

- O bot monitora as cores dos últimos resultados da roleta no Blaze.
- Ele detecta sequências de cores (vermelho/preto) e envia notificações no Telegram.
- Realiza cálculos baseados na estratégia definida, incluindo proteção no branco.

## Arquivos Complementares

- `requirements.txt`: Lista de dependências do Python.
- `bot_blaze.py`: Código principal do bot.

## Contato

Em caso de dúvidas, entre em contato através do repositório GitHub.
