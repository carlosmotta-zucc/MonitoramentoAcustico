"""Funções de processamento do monitoramento acústico.

Reúne, em um só lugar, todas as etapas usadas pelo main.py:
carregamento do WAV, análise no tempo e na frequência (FFT), filtros
FIR/IIR, nível em dB(A) comparado à NBR 10151 e os gráficos.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # backend sem janela: só salva os PNGs
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.signal import (bilinear, butter, filtfilt, find_peaks, firwin,
                          freqz, lfilter, spectrogram)

# --- Pastas ---
PASTA_RAIZ = Path(__file__).resolve().parent.parent
PASTA_AUDIOS = PASTA_RAIZ / "audios"
PASTA_RESULTADOS = PASTA_RAIZ / "resultados"

# --- Análise espectral ---
FS_ESPERADA = 44100      # só para gerar o áudio de teste
N_PICOS = 5              # quantos picos destacar no espectro
ALTURA_MINIMA_PICO = 0.05  # fração do maior pico para considerar um pico
TAMANHO_JANELA = 4096    # janela do espectrograma (amostras)

# --- Filtros ---
FREQ_CORTE = 2000        # corte do passa-baixas (Hz)
ORDEM_IIR = 4            # ordem do Butterworth
NUM_TAPS_FIR = 201       # nº de coeficientes do FIR

# --- Nível de ruído (NBR 10151, entorno universitário) ---
LIMITE_DIURNO = 50       # dB(A)
LIMITE_NOTURNO = 45      # dB(A)
# Sem microfone calibrado o WAV dá só nível relativo (dBFS). Esta constante
# converte dBFS -> dB(A) SPL; medir uma vez contra um decibelímetro.
CALIBRACAO_DB = 100.0


# ======================= CARREGAMENTO =======================

def listar_audios():
    """Devolve, em ordem, os caminhos dos .wav da pasta audios/."""
    return sorted(PASTA_AUDIOS.glob("*.wav"))


def carregar(caminho):
    """Lê um WAV e devolve (sinal_mono, fs), normalizado em [-1, 1]."""
    fs, dados = wavfile.read(caminho)
    sinal = dados.astype(np.float32)
    # WAV inteiro: traz para [-1, 1] dividindo pelo maior valor do tipo.
    if np.issubdtype(dados.dtype, np.integer):
        sinal = sinal / np.iinfo(dados.dtype).max
    # Estéreo vira mono pela média dos canais.
    if sinal.ndim > 1:
        sinal = sinal.mean(axis=1)
    return sinal, fs


# ======================= ANÁLISE (TEMPO E FREQUÊNCIA) =======================

def espectro(sinal, fs):
    """Calcula o espectro de amplitude (FFT) e devolve (frequencias, amplitudes)."""
    n = len(sinal)
    amplitudes = np.abs(np.fft.rfft(sinal)) / n
    frequencias = np.fft.rfftfreq(n, d=1 / fs)
    return frequencias, amplitudes


def picos_predominantes(frequencias, amplitudes):
    """Devolve os N_PICOS picos de maior amplitude como lista de (freq, amp)."""
    altura = ALTURA_MINIMA_PICO * np.max(amplitudes)
    indices, _ = find_peaks(amplitudes, height=altura)
    # Ordena por amplitude (maior primeiro) e fica com os N_PICOS maiores.
    indices = sorted(indices, key=lambda i: amplitudes[i], reverse=True)
    indices = indices[:N_PICOS]
    return [(frequencias[i], amplitudes[i]) for i in indices]


def espectrograma(sinal, fs):
    """Calcula o espectrograma (energia por tempo e frequência)."""
    return spectrogram(sinal, fs=fs, nperseg=TAMANHO_JANELA)


# ======================= FILTROS FIR / IIR =======================

def projetar_iir(fs):
    """Projeta um IIR passa-baixas (Butterworth). Devolve (b, a)."""
    nyquist = fs / 2
    return butter(ORDEM_IIR, FREQ_CORTE / nyquist, btype="low")


def projetar_fir(fs):
    """Projeta um FIR passa-baixas (janela). Devolve (b, a) com a = 1."""
    nyquist = fs / 2
    b = firwin(NUM_TAPS_FIR, FREQ_CORTE / nyquist)
    return b, 1.0


def aplicar_filtro(sinal, b, a):
    """Aplica o filtro ao sinal com fase zero (filtfilt)."""
    return filtfilt(b, a, sinal)


def resposta_frequencia(b, a, fs):
    """Devolve (frequencias, ganho_db) da resposta em frequência do filtro."""
    epsilon = 1e-12
    w, h = freqz(b, a)
    frequencias = w * fs / (2 * np.pi)
    ganho_db = 20 * np.log10(np.abs(h) + epsilon)
    return frequencias, ganho_db


# ======================= NÍVEL EM dB(A) E NORMA =======================

def ponderacao_a(sinal, fs):
    """Aplica a ponderação A (curva da IEC 61672) ao sinal."""
    # Frequências que definem a curva A (Hz) e correção para 0 dB em 1 kHz.
    f1, f2, f3, f4 = 20.598997, 107.65265, 737.86223, 12194.217
    ganho_1khz = 1.9997
    num = [(2 * np.pi * f4) ** 2 * (10 ** (ganho_1khz / 20)), 0, 0, 0, 0]
    den = np.polymul(
        np.polymul([1, 4 * np.pi * f4, (2 * np.pi * f4) ** 2],
                   [1, 4 * np.pi * f1, (2 * np.pi * f1) ** 2]),
        np.polymul([1, 2 * np.pi * f3], [1, 2 * np.pi * f2]),
    )
    b, a = bilinear(num, den, fs)  # filtro analógico -> digital
    return lfilter(b, a, sinal)


def nivel_dba(sinal, fs):
    """Nível em dB(A) SPL aproximado: pondera A -> RMS -> dBFS + calibração."""
    epsilon = 1e-12
    ponderado = ponderacao_a(sinal, fs)
    rms = np.sqrt(np.mean(ponderado ** 2))
    dbfs = 20 * np.log10(rms + epsilon)
    return dbfs + CALIBRACAO_DB


def comparar_norma(nivel, periodo="diurno"):
    """Compara o nível com o limite da NBR 10151. Devolve (limite, situacao)."""
    limite = LIMITE_DIURNO if periodo == "diurno" else LIMITE_NOTURNO
    situacao = "acima" if nivel > limite else "dentro"
    return limite, situacao


# ======================= GRÁFICOS (salvam PNG em resultados/) =======================

def plot_forma_onda(sinal, fs, titulo, nome_arquivo):
    """Plota o sinal no domínio do tempo."""
    tempo = np.arange(len(sinal)) / fs
    figura, eixo = plt.subplots(figsize=(10, 3))
    eixo.plot(tempo, sinal, linewidth=0.5)
    eixo.set_title(titulo)
    eixo.set_xlabel("Tempo (s)")
    eixo.set_ylabel("Amplitude")
    eixo.grid(True, alpha=0.3)
    return _salvar(figura, nome_arquivo)


def plot_espectro(frequencias, amplitudes, picos, titulo, nome_arquivo):
    """Plota o espectro de amplitude e marca os picos predominantes."""
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
    return _salvar(figura, nome_arquivo)


def plot_espectrograma(frequencias, tempos, energia, titulo, nome_arquivo):
    """Plota o espectrograma em escala de dB."""
    epsilon = 1e-12
    figura, eixo = plt.subplots(figsize=(10, 4))
    energia_db = 10 * np.log10(energia + epsilon)
    malha = eixo.pcolormesh(tempos, frequencias, energia_db, shading="gouraud")
    eixo.set_title(titulo)
    eixo.set_xlabel("Tempo (s)")
    eixo.set_ylabel("Frequência (Hz)")
    figura.colorbar(malha, ax=eixo, label="Energia (dB)")
    return _salvar(figura, nome_arquivo)


def plot_resposta_filtros(curvas, titulo, nome_arquivo):
    """Plota a resposta em frequência de um ou mais filtros.

    curvas: lista de (rotulo, frequencias, ganho_db).
    """
    figura, eixo = plt.subplots(figsize=(10, 4))
    for rotulo, frequencias, ganho_db in curvas:
        eixo.plot(frequencias, ganho_db, label=rotulo)
    eixo.set_title(titulo)
    eixo.set_xlabel("Frequência (Hz)")
    eixo.set_ylabel("Ganho (dB)")
    eixo.grid(True, alpha=0.3)
    eixo.legend()
    return _salvar(figura, nome_arquivo)


def plot_comparacao_niveis(nomes, niveis, nome_arquivo):
    """Barras com o nível de cada medição vs. limite diurno da NBR 10151."""
    limite = LIMITE_DIURNO
    figura, eixo = plt.subplots(figsize=(10, 5))
    cores = ["#4caf50" if nivel <= limite else "#e53935" for nivel in niveis]
    eixo.bar(nomes, niveis, color=cores)
    eixo.axhline(limite, color="black", linestyle="--",
                 label=f"Limite NBR ({limite} dB(A))")
    eixo.set_title("Níveis de ruído por medição vs. NBR 10151")
    eixo.set_ylabel("Nível (dB(A))")
    eixo.legend()
    plt.setp(eixo.get_xticklabels(), rotation=30, ha="right")
    return _salvar(figura, nome_arquivo)


def _salvar(figura, nome_arquivo):
    """Salva a figura em resultados/<nome_arquivo> e fecha a figura."""
    caminho = PASTA_RESULTADOS / nome_arquivo
    figura.savefig(caminho, dpi=120, bbox_inches="tight")
    plt.close(figura)
    return caminho
