# Relatório Final – Etapa Prática | Intensivo Maker IoT

### Identificação do Candidato
* **Nome completo:** Caio de Souza Nunes
* **GitHub:** https://github.com/caiionunnes/processoseletivoIoT

---

## Visão Geral da Solução

Sistema embarcado desenvolvido em MicroPython para monitoramento de produção e detecção de micro-paradas em linhas de montagem industriais. O sistema utiliza um sensor óptico (LDR) para contabilizar peças em tempo real e emitir alertas automáticos caso a esteira fique obstruída por mais de 5 segundos. Conta também com um botão físico para reset manual do turno com proteção anti-repique (debounce).

---

## Arquitetura do Sistema Embarcado

O firmware foi estruturado em uma **arquitetura não-bloqueante (evento-direcionada)** para manter a sincronia com os testes automatizados do Wokwi CI, sem travar o processador:

* **Máquina de Estados (FSM):** Alterna entre os estados `LIVRE` (0) e `BLOQUEADO` (1).
* **Controle de Tempo:** O laço principal monitora o tempo continuamente usando `time.ticks_ms()` e `time.ticks_diff()`, evitando o uso de pausas pesadas (`sleep`).
* **Lógica de Detecção:** Utiliza janela de histerese:
  * **Bloqueio:** Leitura do ADC `> 30000` altera o estado para `BLOQUEADO` e inicia o cronômetro.
  * **Contagem:** A peça é incrementada no contador apenas quando a luz retorna (`< 20000`), voltando ao estado `LIVRE`.
* **Alerta de Micro-parada:** Se o tempo contínuo no estado `BLOQUEADO` atingir **5000 ms**, o alarme é disparado via serial.

---

## Componentes Utilizados na Simulação

* **ESP32:** Microcontrolador responsável pela lógica em MicroPython, leitura analógica e logs seriais.
* **Sensor LDR (GPIO 34):** Sensor de passagem da esteira, configurado com atenuação de 11dB (`ADC.ATTN_11DB`) para permitir a faixa completa de leitura de tensão (0 a 65535).
* **Botão Push-Button (GPIO 23):** Botão de reset do turno com resistor pull-up interno (`Pin.PULL_UP`), operando em lógica invertida.

---

## Decisões Técnicas Relevantes

1. **Histerese no Sensor LDR:** Separação entre os limiares de ativação (30000) e desativação (20000) para evitar contagens duplas causadas por ruído elétrico ou oscilação de luz na borda da peça.
2. **Debounce Não-Bloqueante:** Validação do botão por tempo acumulado (50 ms de estabilidade via `time.ticks_diff`), erradicando acionamentos falsos por repique mecânico sem congelar a execução do loop principal.
3. **Padronização Estrita de Saída:** Strings de log impressas via `print()` formatadas exatamente como esperado pelos cenários de teste, cumprindo o critério de validação literal do Wokwi CLI no GitHub Actions.

---

## Resultados Obtidos

* Contagem de peças e emissão de alertas de micro-parada aos 5 segundos operando com 100% de precisão funcional na simulação.
* Ação de reset do botão executando instantaneamente, zerando variáveis e estados com estabilidade.
* Projeto validado e aprovado em todo o pipeline de integração contínua (CI/CD) do GitHub Actions (Testes 1, 2 e 3).

---

## Comentários Adicionais

* **Aprendizados:** O uso da lógica não-bloqueante mostrou-se indispensável para otimizar o uso da CPU e garantir que o firmware responda no tempo exato exigido por esteiras de testes automatizados.
* **Melhorias Futuras:** Implementação de conectividade Wi-Fi/MQTT via ESP32 para envio de relatórios de turno e alarmes de paradas em tempo real para um dashboard IoT em nuvem.