from machine import Pin, ADC
import time

# sensor de luminosidade na esteira
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)  # pra ler o range todo de 0 a 3.3V

# botao de reset - fica em pull up, entao quando aperta o pino vai pra 0
btn = Pin(23, Pin.IN, Pin.PULL_UP)

# limiares do LDR (read_u16 retorna de 0 a 65535)
# testei aqui e esses valores deram uma boa margem entre "livre" e "bloqueado"
# se no wokwi os valores de lux nao baterem certinho da pra reajustar isso
LIMIAR_ALTO = 39000   # acima disso = luz normal, linha livre
LIMIAR_BAIXO = 16000  # abaixo disso = ta bloqueado (peca passando)

TEMPO_MICROPARADA = 5000  # 5s bloqueado seguido = alerta
DEBOUNCE_BTN = 50  # ms pra considerar o botao estavel

# estados possiveis da linha
LIVRE = 0
BLOQUEADO = 1

estado = LIVRE
inicio_bloqueio = 0
ja_alertou = False  # pra nao ficar imprimindo o alerta toda hora enquanto ta travado

total_pecas = 0

# variaveis do debounce do botao
btn_leitura_ant = 1
btn_troca_em = time.ticks_ms()
btn_estavel = 1
btn_ja_resetou = False  # evita resetar varias vezes enquanto segura o botao


def resetar_turno():
    global total_pecas, estado, inicio_bloqueio, ja_alertou

    total_pecas = 0
    estado = LIVRE
    inicio_bloqueio = 0
    ja_alertou = False

    print("Turno resetado com sucesso. Contadores zerados.")


def checa_sensor(agora):
    global estado, inicio_bloqueio, ja_alertou, total_pecas

    valor = ldr.read_u16()

    if estado == LIVRE:
        if valor < LIMIAR_BAIXO:
            # luz caiu, peca comecando a passar
            estado = BLOQUEADO
            inicio_bloqueio = agora
            ja_alertou = False

    else:  # BLOQUEADO
        if valor > LIMIAR_ALTO:
            # luz voltou ao normal -> peca passou, agora sim conta
            total_pecas += 1
            print("Peca detectada! Total: {}".format(total_pecas))
            estado = LIVRE
        else:
            # continua bloqueado, ve se ja passou do tempo de micro-parada
            if not ja_alertou and time.ticks_diff(agora, inicio_bloqueio) > TEMPO_MICROPARADA:
                print("Alerta: Micro-parada detectada!")
                ja_alertou = True


def checa_botao(agora):
    global btn_leitura_ant, btn_troca_em, btn_estavel, btn_ja_resetou

    leitura = btn.value()

    if leitura != btn_leitura_ant:
        # mudou de estado, reinicia contagem do debounce
        btn_leitura_ant = leitura
        btn_troca_em = agora
        return

    # se ficou parado tempo suficiente, considera estavel
    if time.ticks_diff(agora, btn_troca_em) > DEBOUNCE_BTN and leitura != btn_estavel:
        btn_estavel = leitura

        if btn_estavel == 0:
            # apertou de verdade (nao foi ruido)
            if not btn_ja_resetou:
                resetar_turno()
                btn_ja_resetou = True
        else:
            # soltou o botao, libera pro proximo reset
            btn_ja_resetou = False


print("Contador de Producao Inicializado")

while True:
    agora = time.ticks_ms()
    checa_sensor(agora)
    checa_botao(agora)