# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Idioma

Este é um trabalho acadêmico em português (disciplina Análise e Processamento de Sinais). Escreva código, comentários, nomes de variáveis, títulos de gráficos e respostas em português.

## Estado atual

O código **já está implementado** — ver a seção **"Estrutura implementada"** abaixo. Falta apenas o aluno coletar as 4 gravações `.wav` na cantina e colocá-las em `audios/` (hoje a pasta tem só `.gitkeep`). Atualizar esta seção conforme o projeto evoluir.

A pedido do aluno, o código foi **simplificado e consolidado em 2 arquivos** (`processamento.py` + `main.py`), em vez dos vários módulos por etapa planejados originalmente. O `medicoes.csv` foi **removido**: sem metadados, a comparação com a NBR usa sempre o **limite diurno (50 dB(A))**.

## Decisões já tomadas (com o aluno)

- **Aquisição:** os áudios são gravados por fora (ex.: Audacity/celular) e os arquivos `.wav` são colocados manualmente em `audios/`. O código apenas lê e analisa — **não** há gravação ao vivo, portanto **não** usar `sounddevice`/`pyaudio`/portaudio.
- **Organização do código:** o aluno pediu para simplificar e juntar tudo em poucos arquivos — `processamento.py` (todas as funções, agrupadas por etapa com comentários de seção) + `main.py` (orquestrador). As etapas continuam separadas por blocos para facilitar explicar na apresentação.
- **Ambiente-alvo / norma:** entorno universitário → limites de "área de escolas" da NBR 10151: **50 dB(A) diurno / 45 dB(A) noturno**.
- **Bibliotecas:** `numpy` e `scipy` já estão instalados; falta apenas `matplotlib`. Leitura de WAV via `scipy.io.wavfile` (sem dependência de áudio extra).
- **Calibração de dB (importante):** sem microfone calibrado o WAV só fornece nível **relativo (dBFS)**. Para estimar dB(A) SPL, somar uma constante de calibração (`CALIBRACAO_DB`) que o aluno mede uma vez contra uma referência (ex.: app de decibelímetro). Deixar isso explícito no código e no README.

## Estrutura implementada

Estrutura de pastas e arquivos:

```
audios/                  # base de dados acústica: os 4 WAVs do aluno
  .gitkeep
codigo/
  processamento.py       # TODAS as funções (carregar, FFT/picos, espectrograma,
                         #   filtros FIR/IIR, dB(A)/NBR, gráficos) + constantes
  main.py                # orquestra o pipeline em cada .wav de audios/
  gerar_audio_teste.py   # (opcional) gera 4 WAVs sintéticos para testar
  requirements.txt       # numpy, scipy, matplotlib
resultados/              # figuras geradas (PNG) — criada em runtime, ignorada no git
README.md
```

`processamento.py` está dividido em blocos comentados, na ordem das etapas:

- **Constantes** (topo) — caminhos de `audios/`/`resultados/`, params de FFT/filtros, limites NBR (`LIMITE_DIURNO = 50`, `LIMITE_NOTURNO = 45`) e `CALIBRACAO_DB`.
- **Carregamento** — `listar_audios()`; `carregar(caminho)` (lê com `scipy.io.wavfile`, estéreo→mono, normaliza para [-1, 1], retorna `(sinal, fs)`).
- **Análise** — `espectro()` via `numpy.fft.rfft`/`rfftfreq`; `picos_predominantes()` via `scipy.signal.find_peaks`; `espectrograma()` via `scipy.signal.spectrogram`. (RMS e pico são calculados direto no `main.py`.)
- **Filtros** — `projetar_iir()` (`butter`), `projetar_fir()` (`firwin`, devolve `(b, 1.0)`), `aplicar_filtro()` (`filtfilt`, fase zero) e `resposta_frequencia()` (`freqz`).
- **Nível / norma** — `ponderacao_a()` (coeficientes IEC 61672 + `bilinear`); `nivel_dba()` (pondera A → RMS → dBFS + `CALIBRACAO_DB`); `comparar_norma(nivel, periodo="diurno")` (classifica dentro/acima).
- **Gráficos** — `plot_forma_onda`, `plot_espectro` (marcando picos), `plot_espectrograma`, `plot_resposta_filtros` (FIR e IIR juntos), `plot_comparacao_niveis` (barras vs. linha de limite NBR). Salvam PNG em `resultados/` via `_salvar()`.

`main.py` cria `resultados/`, percorre cada WAV (tempo → FFT + picos → espectrograma → filtros FIR/IIR → nível dB(A) → comparação NBR), gera as figuras e imprime a tabela comparativa.

Como rodar:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r codigo/requirements.txt
cd codigo && python main.py
```

Verificação: `python gerar_audio_teste.py` cria 4 WAVs sintéticos com frequências conhecidas em `audios/`; rodar `main.py` e conferir que não há erro, que os PNGs aparecem em `resultados/`, que os picos detectados batem com as frequências usadas e que a tabela de níveis + comparação NBR são impressas.

Mapa entrega → onde é coberta: aquisição/base (1, 2) = `audios/` + `carregar()`; análise espectral (3) = bloco *Análise*; processamento/filtros (4) = bloco *Filtros*; comparação normativa (5) = bloco *Nível / norma*; material de divulgação (7) = bloco *Gráficos*. As entregas 0 (pesquisa) e 6 (apresentação) são textuais/orais, fora do código.

## O que é o projeto (APEx)

"Monitoramento acústico comunitário com análise espectral": atividade de extensão que faz aquisição de áudio ambiental, processamento digital de sinais e análise espectral para diagnosticar ruído em espaços comunitários (escolas, postos de saúde, áreas residenciais, entorno universitário).

Etapas esperadas no código:
- Aquisição de sinais acústicos (mínimo de 4 medições em diferentes períodos/ambientes/condições).
- Análise no domínio do tempo e da frequência (FFT), identificando componentes espectrais predominantes.
- Filtros digitais FIR/IIR para atenuar ruídos ou separar bandas.
- Comparação dos níveis de ruído com referências normativas, quando aplicável.
- Saída acessível à comunidade (gráficos/material de divulgação).

## Estrutura obrigatória

Separar dados de código em duas pastas distintas:
- Uma pasta para os áudios coletados (base de dados acústica).
- Uma pasta separada para o código Python.

## Stack

- Python. Como a aquisição é por WAVs colocados na mão (ver "Decisões já tomadas"), **não** é preciso biblioteca de gravação — a leitura de WAV é feita com `scipy.io.wavfile`.
- `numpy` (FFT, vetores), `scipy.signal` (filtros FIR/IIR, espectrograma, detecção de picos) e `matplotlib` (visualização).

Atualizar aqui o comando de instalação e como executar os scripts assim que o código for implementado.

## Convenções de código (definidas pelo aluno)

Seguir estritamente estas regras ao escrever o código:
- Dentro de cada função, **declarar as constantes primeiro**, com nomes simples.
- Estruturar a lógica priorizando a clareza para explicar o código (o código será apresentado e explicado).
- Manter o código simples, organizado e de fácil manutenção — evitar abstrações e complexidade desnecessárias.
