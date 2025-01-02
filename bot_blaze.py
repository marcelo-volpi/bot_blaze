from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# Configurações do navegador
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--headless")  # Ativa o modo headless

# Inicializar navegador
nav = webdriver.Chrome(options=chrome_options)

# Mensagens de status
msg_ativo = "✅ Bot Ativo"
aviso_4_generico = "⚠️ Atenção para entrada na cor oposta: "
aviso_falso = "🚫 Alarme falso: padrão quebrado."
sinal_vermelho = "🔴 Sequência de 5 Vermelhos - Entrar no Preto."
sinal_preto = "⚫ Sequência de 5 Pretos - Entrar no Vermelho."
sinal_gale = "📢 Fazer Gale - Repetindo entrada."
proteger_branco_7 = "⚪ Proteger patrimônio com 7% no Branco."
proteger_branco_14 = "⚪ Proteger patrimônio com 14% no Branco."
msg_encerrado = "❌ Bot Encerrado"

# Configuração do Telegram
token = "5489024933:AAEqYViiJSnwcfs_YDpGY-VDWrLlJOepBAE"
chat_id = "-1001599159882"

# Função para enviar mensagem no Telegram
def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": mensagem}
    try:
        requests.post(url, data)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# Variáveis globais para controle
historico_cores = []
fazendo_gale = False
ultima_lista = []  # Armazena a última lista capturada
alertado_4 = False
banca = 260  # Banca inicial em reais
aposta = 20  # Valor da aposta inicial
vitorias = 0
perdas = 0
resetar_entrada = False  # Variável para resetar padrão após conclusão de Gale
primeira_entrada_feita = False  # Controla se a primeira entrada foi feita

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
    global fazendo_gale, alertado_4, banca, aposta, vitorias, perdas, resetar_entrada, primeira_entrada_feita

    # Valor de proteção no branco (7% da aposta)
    protecao_branco_7 = aposta * 0.07
    protecao_branco_14 = (aposta * 2) * 0.14

    # Reseta o estado caso o padrão tenha sido concluído
    if resetar_entrada:
        print("Aguardando novo padrão para entrar.")
        if cores[-5:] != ["Vermelho"] * 5 and cores[-5:] != ["Preto"] * 5:
            resetar_entrada = False
            primeira_entrada_feita = False
            print("Novo padrão detectado. Pronto para novas entradas.")
        return

    # Verifica se há 4 cores consecutivas e envia alerta apenas uma vez
    if cores[-4:] == ["Vermelho"] * 4 and not alertado_4 and not primeira_entrada_feita:
        print(aviso_4_generico + "Preto")
        enviar_mensagem(aviso_4_generico + "Preto")
        alertado_4 = True
    elif cores[-4:] == ["Preto"] * 4 and not alertado_4 and not primeira_entrada_feita:
        print(aviso_4_generico + "Vermelho")
        enviar_mensagem(aviso_4_generico + "Vermelho")
        alertado_4 = True

    # Verifica se a sequência foi interrompida antes de 5 cores iguais
    if alertado_4 and cores[-5:] != ["Vermelho"] * 5 and cores[-5:] != ["Preto"] * 5:
        print(aviso_falso)
        enviar_mensagem(aviso_falso)
        alertado_4 = False

    # Verifica se há 5 cores consecutivas para entrada
    if cores[-5:] == ["Vermelho"] * 5 and not primeira_entrada_feita:
        print(sinal_vermelho)
        enviar_mensagem(sinal_vermelho)
        enviar_mensagem(proteger_branco_7)
        alertado_4 = False  # Reseta o alerta de 4
        primeira_entrada_feita = True
        banca -= aposta + protecao_branco_7  # Reduz o valor apostado e a proteção da banca
        # Simula resultado da aposta
        if cores[-1] == "Preto":
            ganho = aposta * 2 - protecao_branco_7
            banca += ganho
            vitorias += 1
            print(f"✅ Vitória! Banca atual: R${banca:.2f}")
            enviar_mensagem(f"✅ Vitória! Banca atual: R${banca:.2f}")
            resetar_entrada = True  # Define para esperar novo padrão
        elif cores[-1] == "Branco":
            ganho_branco = protecao_branco_7 * 14
            banca += ganho_branco
            print(f"⚪ Vitória no Branco! Ganhou R${ganho_branco:.2f}. Banca atual: R${banca:.2f}")
            enviar_mensagem(f"⚪ Vitória no Branco! Ganhou R${ganho_branco:.2f}. Banca atual: R${banca:.2f}")
            resetar_entrada = True
        else:
            fazendo_gale = True

    elif cores[-5:] == ["Preto"] * 5 and not primeira_entrada_feita:
        print(sinal_preto)
        enviar_mensagem(sinal_preto)
        enviar_mensagem(proteger_branco_7)
        alertado_4 = False  # Reseta o alerta de 4
        primeira_entrada_feita = True
        banca -= aposta + protecao_branco_7  # Reduz o valor apostado e a proteção da banca
        # Simula resultado da aposta
        if cores[-1] == "Vermelho":
            ganho = aposta * 2 - protecao_branco_7
            banca += ganho
            vitorias += 1
            print(f"✅ Vitória! Banca atual: R${banca:.2f}")
            enviar_mensagem(f"✅ Vitória! Banca atual: R${banca:.2f}")
            resetar_entrada = True  # Define para esperar novo padrão
        elif cores[-1] == "Branco":
            ganho_branco = protecao_branco_7 * 14
            banca += ganho_branco
            print(f"⚪ Vitória no Branco! Ganhou R${ganho_branco:.2f}. Banca atual: R${banca:.2f}")
            enviar_mensagem(f"⚪ Vitória no Branco! Ganhou R${ganho_branco:.2f}. Banca atual: R${banca:.2f}")
            resetar_entrada = True
        else:
            fazendo_gale = True

    # Verifica Gale ativo
    elif fazendo_gale:
        enviar_mensagem(proteger_branco_14)
        banca -= (aposta * 2) + protecao_branco_14  # Reduz o valor do Gale e proteção da banca
        if cores[-1] == "Preto" or cores[-1] == "Vermelho":
            ganho = (aposta * 4) - protecao_branco_14
            banca += ganho
            vitorias += 1
            print(f"✅ Vitória no Gale! Banca atual: R${banca:.2f}")
            enviar_mensagem(f"✅ Vitória no Gale! Banca atual: R${banca:.2f}")
            fazendo_gale = False
            resetar_entrada = True  # Define para esperar novo padrão
        elif cores[-1] == "Branco":
            ganho_branco = protecao_branco_14 * 14
            banca += ganho_branco
            print(f"⚪ Vitória no Branco durante Gale! Ganhou R${ganho_branco:.2f}. Banca atual: R${banca:.2f}")
            enviar_mensagem(f"⚪ Vitória no Branco durante Gale! Ganhou R${ganho_branco:.2f}. Banca atual: R${banca:.2f}")
            fazendo_gale = False
            resetar_entrada = True
        else:
            perdas += 1
            print(f"❌ Perda no Gale! Banca atual: R${banca:.2f}")
            enviar_mensagem(f"❌ Perda no Gale! Banca atual: R${banca:.2f}")
            fazendo_gale = False
            resetar_entrada = True

    # Exibir estatísticas apenas após vitória ou derrota final
    if primeira_entrada_feita and (not fazendo_gale or resetar_entrada):
        total_tentativas = vitorias + perdas
        if total_tentativas > 0:
            porcentagem_vitorias = (vitorias / total_tentativas) * 100
            porcentagem_perdas = (perdas / total_tentativas) * 100
            print(f"📊 Estatísticas: {vitorias} Vitórias ({porcentagem_vitorias:.2f}%), {perdas} Derrotas ({porcentagem_perdas:.2f}%)")
            enviar_mensagem(f"📊 Estatísticas: {vitorias} Vitórias ({porcentagem_vitorias:.2f}%), {perdas} Derrotas ({porcentagem_perdas:.2f}%)")

# Comparar listas para verificar alterações
def lista_alterada(nova_lista):
    global ultima_lista
    if nova_lista != ultima_lista:
        ultima_lista = nova_lista
        return True
    return False

# Loop principal com tratamento de erros
try:
    acessar_pagina()
    for _ in range(2880):  # Aproximadamente 24 horas com intervalos de 30 segundos
        print("Iniciando nova iteração do loop...")
        resultados = capturar_resultados()
        if resultados and lista_alterada(resultados):
            historico_cores.extend(resultados)  # Atualiza o histórico
            historico_cores = historico_cores[-10:]  # Mantém apenas os últimos 10
            verificar_padroes(historico_cores)
        else:
            print("Nenhuma alteração na lista capturada.")
        time.sleep(7)  # Intervalo reduzido para depuração
except Exception as e:
    erro_msg = f"❌ Bot encerrado devido a um erro: {e}"
    print(erro_msg)
    enviar_mensagem(erro_msg)
finally:
    # Mensagem de encerramento ao finalizar
    print(msg_encerrado)
    enviar_mensagem(msg_encerrado)
    nav.quit()
