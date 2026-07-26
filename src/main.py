from machine import Pin, ADC
import time

ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)

btn = Pin(23, Pin.IN, Pin.PULL_UP)

# sensor e invertido: mais luz = adc menor (testei no wokwi, 100k lux deu 512 e quase sem luz deu 65023)
LIMIAR_LIVRE = 27000
LIMIAR_BLOQUEIO = 33000

TEMPO_MICROPARADA = 5000
DEBOUNCE_BTN = 50

LIVRE = 0
BLOQUEADO = 1

estado = LIVRE
inicio_bloqueio = 0
ja_alertou = False

total_pecas = 0

btn_leitura_ant = 1
btn_troca_em = time.ticks_ms()
btn_estavel = 1
btn_ja_resetou = False


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
        if valor > LIMIAR_BLOQUEIO:
            estado = BLOQUEADO
            inicio_bloqueio = agora
            ja_alertou = False

    else:
        if valor < LIMIAR_LIVRE:
            total_pecas += 1
            print("Peca detectada! Total: {}".format(total_pecas))
            estado = LIVRE
        else:
            if not ja_alertou and time.ticks_diff(agora, inicio_bloqueio) > TEMPO_MICROPARADA:
                print("Alerta: Micro-parada detectada!")
                ja_alertou = True


def checa_botao(agora):
    global btn_leitura_ant, btn_troca_em, btn_estavel, btn_ja_resetou

    leitura = btn.value()

    if leitura != btn_leitura_ant:
        btn_leitura_ant = leitura
        btn_troca_em = agora
        return

    if time.ticks_diff(agora, btn_troca_em) > DEBOUNCE_BTN and leitura != btn_estavel:
        btn_estavel = leitura

        if btn_estavel == 0:
            if not btn_ja_resetou:
                resetar_turno()
                btn_ja_resetou = True
        else:
            btn_ja_resetou = False


print("Contador de Producao Inicializado")

while True:
    agora = time.ticks_ms()
    checa_sensor(agora)
    checa_botao(agora)