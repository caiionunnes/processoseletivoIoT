from machine import Pin, ADC
import time

# --- CONFIGURAÇÃO DO HARDWARE ---
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)

btn = Pin(23, Pin.IN, Pin.PULL_UP)

# --- LIMIARES DO SENSOR ---
# Mais luz = ADC menor
# Menos luz = ADC maior

LIMIAR_LIVRE = 20000
LIMIAR_BLOQUEIO = 30000

# --- PARÂMETROS ---
TEMPO_MICROPARADA = 5000
DEBOUNCE_BTN = 50

# --- ESTADOS ---
LIVRE = 0
BLOQUEADO = 1

estado = LIVRE
inicio_bloqueio = 0
ja_alertou = False

# --- CONTADOR ---
total_pecas = 0

# --- CONTROLE DO BOTÃO ---
btn_leitura_ant = btn.value()
btn_troca_em = time.ticks_ms()
btn_estavel = btn.value()
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

    # Linha livre
    if estado == LIVRE:

        # Luz caiu: objeto bloqueou o sensor
        if valor > LIMIAR_BLOQUEIO:
            estado = BLOQUEADO
            inicio_bloqueio = agora
            ja_alertou = False

    # Peça bloqueando o sensor
    else:

        # Luz voltou: peça passou completamente
        if valor < LIMIAR_LIVRE:
            total_pecas += 1

            print("Peca detectada! Total: {}".format(total_pecas))

            estado = LIVRE

        # Continua bloqueado
        else:
            if (
                not ja_alertou
                and time.ticks_diff(agora, inicio_bloqueio)
                >= TEMPO_MICROPARADA
            ):
                print("Alerta: Micro-parada detectada!")
                ja_alertou = True


def checa_botao(agora):
    global btn_leitura_ant
    global btn_troca_em
    global btn_estavel
    global btn_ja_resetou

    leitura = btn.value()

    # Detectou mudança de estado
    if leitura != btn_leitura_ant:
        btn_leitura_ant = leitura
        btn_troca_em = agora
        return

    # Aguarda o estado permanecer estável durante o debounce
    if time.ticks_diff(agora, btn_troca_em) >= DEBOUNCE_BTN:

        if leitura != btn_estavel:
            btn_estavel = leitura

            # Botão pressionado
            if btn_estavel == 0:

                if not btn_ja_resetou:
                    resetar_turno()
                    btn_ja_resetou = True

            # Botão liberado
            elif btn_estavel == 1:

                btn_ja_resetou = False


# --- INICIALIZAÇÃO ---
print("Contador de Producao Inicializado")


# --- LOOP PRINCIPAL ---
while True:
    agora = time.ticks_ms()

    checa_sensor(agora)
    checa_botao(agora)

    # Pequena pausa para evitar uso excessivo da CPU
    time.sleep_ms(5)