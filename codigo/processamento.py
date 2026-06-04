# Funções de processamento do monitoramento acústico.

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # só salva os PNGs, não abre janela
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, find_peaks, firwin, freqz, spectrogram

# Pastas
PASTA_RAIZ = Path(__file__).resolve().parent.parent
PASTA_AUDIOS = PASTA_RAIZ / "audios"
PASTA_RESULTADOS = PASTA_RAIZ / "resultados"

# Análise espectral
N_PICOS = 5                # quantos picos destacar no espectro
ALTURA_MINIMA_PICO = 0.05  # fração do maior pico para considerar um pico
TAMANHO_JANELA = 4096      # janela do espectrograma (amostras)

# Filtros
FREQ_CORTE = 2000          # corte do passa-baixas (Hz)
ORDEM_IIR = 4              # ordem do Butterworth
NUM_TAPS_FIR = 201         # nº de coeficientes do FIR

# Nível de ruído (NBR 10151, entorno universitário)
LIMITE_DIURNO = 50         # dB(A)
LIMITE_NOTURNO = 45        # dB(A)
# Sem microfone calibrado o WAV dá só nível relativo (dBFS). Esta constante
# converte dBFS -> dB SPL; medir uma vez contra um decibelímetro.
CALIBRACAO_DB = 100.0


# Lista os caminhos dos .wav da pasta audios/.
def listar_audios():
    return sorted(PASTA_AUDIOS.glob("*.wav"))


# Lê um WAV e devolve (sinal mono, fs) normalizado em [-1, 1].
def carregar(caminho):
    fs, dados = wavfile.read(caminho)
    sinal = dados.astype(np.float32)
    if np.issubdtype(dados.dtype, np.integer):
        sinal = sinal / np.iinfo(dados.dtype).max
    if sinal.ndim > 1:
        sinal = sinal.mean(axis=1)  # estéreo -> mono
    return sinal, fs


# Espectro de amplitude (FFT): devolve (frequencias, amplitudes).
def espectro(sinal, fs):
    n = len(sinal)
    amplitudes = np.abs(np.fft.rfft(sinal)) / n
    frequencias = np.fft.rfftfreq(n, d=1 / fs)
    return frequencias, amplitudes


# Devolve os N_PICOS picos de maior amplitude como lista de (freq, amp).
def picos_predominantes(frequencias, amplitudes):
    altura = ALTURA_MINIMA_PICO * np.max(amplitudes)
    indices, _ = find_peaks(amplitudes, height=altura)
    indices = sorted(indices, key=lambda i: amplitudes[i], reverse=True)
    indices = indices[:N_PICOS]
    return [(frequencias[i], amplitudes[i]) for i in indices]


# Espectrograma (energia por tempo e frequência).
def espectrograma(sinal, fs):
    return spectrogram(sinal, fs=fs, nperseg=TAMANHO_JANELA)


# Projeta um IIR passa-baixas (Butterworth). Devolve (b, a).
def projetar_iir(fs):
    nyquist = fs / 2
    return butter(ORDEM_IIR, FREQ_CORTE / nyquist, btype="low")


# Projeta um FIR passa-baixas (janela). Devolve (b, a) com a = 1.
def projetar_fir(fs):
    nyquist = fs / 2
    b = firwin(NUM_TAPS_FIR, FREQ_CORTE / nyquist)
    return b, 1.0


# Aplica o filtro ao sinal com fase zero.
def aplicar_filtro(sinal, b, a):
    return filtfilt(b, a, sinal)


# Resposta em frequência do filtro: devolve (frequencias, ganho_db).
def resposta_frequencia(b, a, fs):
    w, h = freqz(b, a)
    frequencias = w * fs / (2 * np.pi)
    ganho_db = 20 * np.log10(np.abs(h) + 1e-12)
    return frequencias, ganho_db


# Nível aproximado em dB: RMS -> dBFS + calibração (sem ponderação A).
def nivel_db(sinal):
    rms = np.sqrt(np.mean(sinal ** 2))
    dbfs = 20 * np.log10(rms + 1e-12)
    return dbfs + CALIBRACAO_DB


# Compara o nível com o limite da NBR 10151. Devolve (limite, situacao).
def comparar_norma(nivel, periodo="diurno"):
    limite = LIMITE_DIURNO if periodo == "diurno" else LIMITE_NOTURNO
    situacao = "acima" if nivel > limite else "dentro"
    return limite, situacao


# Plota o sinal no domínio do tempo.
def plot_forma_onda(sinal, fs, titulo, nome_arquivo):
    tempo = np.arange(len(sinal)) / fs
    figura, eixo = plt.subplots(figsize=(10, 3))
    eixo.plot(tempo, sinal, linewidth=0.5)
    eixo.set_title(titulo)
    eixo.set_xlabel("Tempo (s)")
    eixo.set_ylabel("Amplitude")
    eixo.grid(True, alpha=0.3)
    salvar(figura, nome_arquivo)


# Plota o espectro de amplitude e marca os picos predominantes.
def plot_espectro(frequencias, amplitudes, picos, titulo, nome_arquivo):
    figura, eixo = plt.subplots(figsize=(10, 4))
    eixo.plot(frequencias, amplitudes, linewidth=0.7)
    for frequencia, amplitude in picos:
        eixo.plot(frequencia, amplitude, "ro")
        eixo.annotate(f"{frequencia:.0f} Hz", (frequencia, amplitude),
                      textcoords="offset points", xytext=(5, 5), fontsize=8)
    eixo.set_title(titulo)
    eixo.set_xlabel("Frequência (Hz)")
    eixo.set_ylabel("Amplitude")
    eixo.grid(True, alpha=0.3)
    salvar(figura, nome_arquivo)


# Plota o espectrograma em escala de dB.
def plot_espectrograma(frequencias, tempos, energia, titulo, nome_arquivo):
    figura, eixo = plt.subplots(figsize=(10, 4))
    energia_db = 10 * np.log10(energia + 1e-12)
    malha = eixo.pcolormesh(tempos, frequencias, energia_db, shading="gouraud")
    eixo.set_title(titulo)
    eixo.set_xlabel("Tempo (s)")
    eixo.set_ylabel("Frequência (Hz)")
    figura.colorbar(malha, ax=eixo, label="Energia (dB)")
    salvar(figura, nome_arquivo)


# Plota a resposta em frequência de um ou mais filtros.
# curvas: lista de (rotulo, frequencias, ganho_db).
def plot_resposta_filtros(curvas, titulo, nome_arquivo):
    figura, eixo = plt.subplots(figsize=(10, 4))
    for rotulo, frequencias, ganho_db in curvas:
        eixo.plot(frequencias, ganho_db, label=rotulo)
    eixo.set_title(titulo)
    eixo.set_xlabel("Frequência (Hz)")
    eixo.set_ylabel("Ganho (dB)")
    eixo.grid(True, alpha=0.3)
    eixo.legend()
    salvar(figura, nome_arquivo)


# Barras com o nível de cada medição vs. limite diurno da NBR 10151.
def plot_comparacao_niveis(nomes, niveis, nome_arquivo):
    limite = LIMITE_DIURNO
    figura, eixo = plt.subplots(figsize=(10, 5))
    cores = ["green" if nivel <= limite else "red" for nivel in niveis]
    eixo.bar(nomes, niveis, color=cores)
    eixo.axhline(limite, color="black", linestyle="--",
                 label=f"Limite NBR ({limite} dB(A))")
    eixo.set_title("Níveis de ruído por medição vs. NBR 10151")
    eixo.set_ylabel("Nível (dB)")
    eixo.legend()
    plt.setp(eixo.get_xticklabels(), rotation=30, ha="right")
    salvar(figura, nome_arquivo)


# Salva a figura em resultados/ e fecha.
def salvar(figura, nome_arquivo):
    figura.savefig(PASTA_RESULTADOS / nome_arquivo, dpi=120, bbox_inches="tight")
    plt.close(figura)
