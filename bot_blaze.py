from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from dotenv import load_dotenv
import os

# Carrega as variáveis do .env
load_dotenv()

# Configurações do navegador
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--headless")  # Ativa o modo headless

# Inicializar navegador
nav = webdriver.Chrome(options=chrome_options)

# Mensagens de status
msg_ativo = "✅ Bot Ativo"
aviso_generico = "⚠️ Atenção para entrada na cor oposta:  "
aviso_falso = "🚫 Alarme falso: Aguardando novo padrão 🚫"
sinal_vermelho = "⚫⚫ Atenção: Entrar no Preto \n⚫⚫"
sinal_preto = "🔴🔴 Atenção entrar no Vermelho 🔴🔴"
sinal_gale = "📢 GALE - Duplicar aposta repetindo a entrada."
proteger_branco_10 = "⚪ Proteger patrimônio com 10% no Branco."
msg_encerrado = "❌ Bot Encerrado"

# Configuração do Telegram
token = os.getenv("TOKEN_TELEGRAM")
chat_id = os.getenv("CHAT_ID")

# Variáveis configuráveis pelo usuário
sequencia_para_entrada = 5  # Configuração inicial: 3 cores iguais para entrada
notificacoes_ativas = True  # Variável para ativar/desativar notificações do Telegram

# Função para enviar mensagem no Telegram
def enviar_mensagem(mensagem):
    if notificacoes_ativas:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": mensagem}
        try:
            requests.post(url, data)
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
    else:
        print(f"Notificação desativada: {mensagem}")

# Variáveis globais para controle
historico_cores = []
fazendo_gale = False
ultima_lista = []  # Armazena a última lista capturada
alertado = False
entrada_realizada = False  # Controla se a entrada foi realizada
banca = 1000  # Banca inicial em reais
aposta = 50  # Valor da aposta inicial
vitorias = 0
perdas = 0
aguardando_resultado = False  # Variável para aguardar o próximo giro após entrada
resetar_entrada = False  # Variável para resetar padrão após conclusão de Gale
cor_da_entrada = None  # Armazena a cor da entrada para verificar vitória
banca_inicial = banca  # Armazena o valor inicial da banca para cálculo de vitórias e derrotas
contador_atualizado = False  # Garante que vitória ou derrota seja contabilizada apenas uma vez
ganho_acumulado = 0  # Acumula os ganhos totais

# Acessar a página do jogo
def acessar_pagina():
    nav.get('https://blaze.bet.br/pt/games/double')
    try:
        WebDriverWait(nav, 10).until(
            EC.presence_of_element_located((By.ID, 'roulette-recent'))
        )
        print("Página acessada com sucesso e conteúdo carregado.")
        enviar_mensagem(msg_ativo)
    except Exception as e:
        print(f"Erro ao carregar a página: {e}")

# Capturar resultados da roleta com base na cor
def capturar_resultados():
    try:
        container = nav.find_element(By.ID, 'roulette-recent')  # Localiza o container principal
        print(f"Conteúdo do container: {container.text}")
        
        # Localiza os elementos das cores
        elementos = container.find_elements(By.CLASS_NAME, 'sm-box')
        resultados = []
        for e in elementos[:10]:  # Captura os últimos 10 resultados
            classe = e.get_attribute('class')
            if 'red' in classe:
                resultados.append('Vermelho')
            elif 'black' in classe:
                resultados.append('Preto')
            elif 'white' in classe:
                resultados.append('Branco')
            else:
                resultados.append('Desconhecido')
        resultados.reverse()  # Inverte para que a ordem seja da direita para a esquerda
        print(f"Resultados capturados: {resultados}")
        return resultados
    except Exception as e:
        print(f"Erro ao capturar resultados: {e}")
        return []

# Verificar padrões e enviar sinais
def verificar_padroes(cores):
    global fazendo_gale, alertado, entrada_realizada, aguardando_resultado, banca, aposta, vitorias, perdas, resetar_entrada, cor_da_entrada, banca_inicial, contador_atualizado, ganho_acumulado

    # Valor de proteção no branco (10% da aposta)
    protecao_branco = aposta * 0.10

    # Reset do estado somente após vitória, derrota ou alarme falso
    if resetar_entrada:
        print("♻️ Resetando padrão após conclusão do ciclo anterior.")
        print(f"Antes do reset: alertado={alertado}, entrada_realizada={entrada_realizada}, aguardando_resultado={aguardando_resultado}, cor_da_entrada={cor_da_entrada}")
        resetar_entrada = False
        entrada_realizada = False
        alertado = False
        aguardando_resultado = False
        cor_da_entrada = None
        contador_atualizado = False
        print(f"Após o reset: alertado={alertado}, entrada_realizada={entrada_realizada}, aguardando_resultado={aguardando_resultado}, cor_da_entrada={cor_da_entrada}")
        return

    # Aguardar o próximo resultado após entrada
    if aguardando_resultado:
        if cores[-1] == cor_da_entrada:  # Vitória
            ganho = aposta * 2
            lucro = ganho - (protecao_branco + aposta)  # Calcula o lucro líquido
            banca += lucro  # Atualiza a banca com o lucro da entrada
            ganho_acumulado = banca - banca_inicial  # Recalcula o ganho acumulado
            if not contador_atualizado:
                vitorias += 1
                contador_atualizado = True
            percentual_vitorias = (vitorias / (vitorias + perdas)) * 100 if (vitorias + perdas) > 0 else 0
            print(f"✅✅✅ Vitória! ✅✅")
            print(f"📊 Banca atual: R${banca:.2f}, Ganho acumulado: R${ganho_acumulado:.2f}")
            enviar_mensagem(f"✅✅✅ Vitória! ✅✅\n📊 Banca atual: R${banca:.2f}\n🏆 Vitórias: {vitorias} ({percentual_vitorias:.2f}% de sucesso)\n💰 Ganho acumulado: R${ganho_acumulado:.2f}")
            resetar_entrada = True
            return  # Interrompe o fluxo após vitória

        elif cores[-1] == "Branco":  # Branco
            ganho_branco = protecao_branco * 14  # Branco paga 14 vezes o valor apostado
            lucro = ganho_branco - (aposta + protecao_branco)
            banca += lucro  # Atualiza a banca
            ganho_acumulado = banca - banca_inicial  # Recalcula o ganho acumulado
            if not contador_atualizado:
                if lucro > 0:
                    vitorias += 1
                    percentual_vitorias = (vitorias / (vitorias + perdas)) * 100 if (vitorias + perdas) > 0 else 0
                    print(f"⚪ Branco! Lucro desta entrada: R${lucro:.2f}.")
                    print(f"📊 Banca atual: R${banca:.2f}, Ganho acumulado: R${ganho_acumulado:.2f}")
                    enviar_mensagem(f"⚪ Branco! Lucro desta entrada: R${lucro:.2f}.\n📊 Banca atual: R${banca:.2f}\n🏆 Vitórias: {vitorias} ({percentual_vitorias:.2f}% de sucesso)\n💰 Ganho acumulado: R${ganho_acumulado:.2f}")
                    contador_atualizado = True
                elif lucro < 0:
                    print(f"⚪ Branco! Redução de perdas.")
                    print(f"📉 Banca atual: R${banca:.2f}")
                    enviar_mensagem(f"⚪ Branco! Redução de perdas.\n📉 Banca atual: R${banca:.2f}")
                    contador_atualizado = True
            resetar_entrada = True
            return  # Interrompe o fluxo após proteção no Branco

        elif cores[-1] != cor_da_entrada:  # Derrota no Gale ou entrada inicial
            perda = aposta + protecao_branco
            banca -= perda  # Subtrai a perda da banca
            ganho_acumulado = banca - banca_inicial  # Recalcula o ganho acumulado

            if fazendo_gale:  # Gale ativo
                perdas += 1
                print(f"🚫 Derrota no Gale.")
                print(f"📉 Banca atual após Gale: R${banca:.2f}, Ganho acumulado: R${ganho_acumulado:.2f}")
                enviar_mensagem(f"🚫 Derrota no Gale.\n📉 Banca atual: R${banca:.2f}\n💰 Ganho acumulado: R${ganho_acumulado:.2f}")
                resetar_entrada = True  # Finaliza o Gale
                fazendo_gale = False  # Reseta o estado do Gale
                aposta = 50  # Reseta o valor da aposta inicial
                return  # Interrompe o fluxo após derrota no Gale

            else:  # Primeira tentativa, inicia Gale
                print("🚫 Derrota inicial. Iniciando Gale.")
                print(sinal_gale)
                print(proteger_branco_10)
                enviar_mensagem(sinal_gale)
                enviar_mensagem(proteger_branco_10)
                fazendo_gale = True  # Ativa o estado do Gale
                aposta *= 2  # Dobra o valor da aposta para o Gale
                aguardando_resultado = True  # Mantém o estado para o próximo giro
                return  # Interrompe o fluxo após ativar o Gale



    # Verifica se há n-1 cores consecutivas e envia alerta apenas uma vez
    if not alertado and not entrada_realizada:
        if cores[-(sequencia_para_entrada-1):] == ["Vermelho"] * (sequencia_para_entrada-1):
            print(aviso_generico + "Preto")
            print(proteger_branco_10)
            enviar_mensagem(aviso_generico + "Preto")
            enviar_mensagem(proteger_branco_10)
            alertado = True
        elif cores[-(sequencia_para_entrada-1):] == ["Preto"] * (sequencia_para_entrada-1):
            print(aviso_generico + "Vermelho")
            print(proteger_branco_10)
            enviar_mensagem(aviso_generico + "Vermelho")
            enviar_mensagem(proteger_branco_10)
            alertado = True

    # Verifica se há n-1 cores iguais + 1 cor diferente (alarme falso)
    if alertado and not entrada_realizada:
        if cores[-sequencia_para_entrada:-1] == ["Vermelho"] * (sequencia_para_entrada-1) and cores[-1] != "Vermelho":
            print(aviso_falso)
            enviar_mensagem(aviso_falso)
            resetar_entrada = True
            alertado = False  # Reseta o estado do alerta para permitir novos padrões
            entrada_realizada = False  # Reseta o padrão para novas entradas

        elif cores[-sequencia_para_entrada:-1] == ["Preto"] * (sequencia_para_entrada-1) and cores[-1] != "Preto":
            print(aviso_falso)
            enviar_mensagem(aviso_falso)
            resetar_entrada = True
            alertado = False  # Reseta o estado do alerta para permitir novos padrões
            entrada_realizada = False  # Reseta o padrão para novas entradas  

    # Verifica se há n cores consecutivas para realizar entrada
    if alertado and not entrada_realizada:
        if cores[-sequencia_para_entrada:] == ["Vermelho"] * sequencia_para_entrada:
            print(sinal_vermelho)
            enviar_mensagem(sinal_vermelho)
            entrada_realizada = True
            cor_da_entrada = "Preto"  # Entrada será no Preto
            aguardando_resultado = True
        elif cores[-sequencia_para_entrada:] == ["Preto"] * sequencia_para_entrada:
            print(sinal_preto)
            enviar_mensagem(sinal_preto)
            entrada_realizada = True
            cor_da_entrada = "Vermelho"  # Entrada será no Vermelho
            aguardando_resultado = True

# Início do programa
try:
    acessar_pagina()
    while True:
        print("Iniciando nova iteração do loop...")
        resultados = capturar_resultados()
        if resultados and resultados != ultima_lista:
            ultima_lista = resultados
            verificar_padroes(resultados)
        else:
            print("Nenhuma alteração na lista capturada.")
        time.sleep(5)
except Exception as e:
    print(f"❌ Erro: {e}")
finally:
    print(msg_encerrado)
    enviar_mensagem(msg_encerrado)
    nav.quit()
