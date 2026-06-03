# Monitoramento acústico comunitário com análise espectral (APEx)

Projeto da disciplina **Análise e Processamento de Sinais**. Faz a aquisição
de áudio ambiental, processamento digital e análise espectral para
diagnosticar o ruído em um espaço comunitário.

**Ambiente analisado:** cantina de uma faculdade (4 medições).

## Organização

```
audios/        # base de dados acústica: coloque aqui os 4 arquivos .wav
codigo/        # código Python
resultados/    # figuras PNG geradas ao rodar (criada automaticamente)
```

| Arquivo (em `codigo/`) | Responsabilidade |
|------------------------|------------------|
| `processamento.py`     | Todas as funções: ler WAV, FFT/picos, espectrograma, filtros FIR/IIR, nível em dB(A), NBR e gráficos |
| `main.py`              | Orquestra o pipeline em cada `.wav` de `audios/` |
| `gerar_audio_teste.py` | (opcional) Gera 4 WAVs sintéticos para testar o pipeline |

## Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r codigo/requirements.txt

cd codigo
python main.py
```

O `main.py` lê todos os `.wav` de `audios/`, gera as figuras em `resultados/`
e imprime no terminal uma tabela comparando os níveis com a NBR 10151.

## Aquisição dos áudios

As gravações são feitas **por fora** (ex.: Audacity) e os 4 arquivos `.wav`
são colocados manualmente em `audios/`. O código apenas lê e analisa — não há
gravação ao vivo.

Configuração usada na captura (Audacity):

- Dispositivo de gravação: microfone do headset (PortAudio/ALSA)
- Canais: 2 (estéreo) — o código converte para mono pela média dos canais
- Taxa de amostragem: 44100 Hz
- Formato: 32-bit float

## Calibração do nível em dB(A)

Sem um microfone calibrado, o WAV fornece apenas nível **relativo (dBFS)**.
Para estimar o **dB(A) SPL**, o código soma a constante `CALIBRACAO_DB`
(no início de `processamento.py`). Meça-a uma vez: grave um som e, ao mesmo
tempo, anote o valor de um decibelímetro de referência (ex.: app de celular);
ajuste `CALIBRACAO_DB` até o nível calculado bater com o medido.

## Referência normativa

NBR 10151 — limite para "área de escolas" / entorno universitário usado na
comparação: **50 dB(A) (diurno)**. O limite noturno (45 dB(A)) também está
em `processamento.py`, caso queira tratar medições noturnas.

## Teste rápido (sem gravações reais)

```bash
cd codigo
python gerar_audio_teste.py   # cria audios/cantina_1..4.wav (frequências conhecidas)
python main.py                # deve detectar esses picos e salvar os PNGs
```
