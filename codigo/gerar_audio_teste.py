"""Gera 4 WAVs sintéticos para testar o pipeline antes das gravações reais.

Cada arquivo tem senoides em frequências conhecidas somadas a um ruído
fraco. Serve para conferir que o main.py roda sem erro, que os PNGs
aparecem em resultados/ e que os picos detectados batem com as
frequências usadas aqui.

Como rodar (a partir da pasta codigo/):  python gerar_audio_teste.py
"""

import numpy as np
from scipy.io import wavfile

from processamento import PASTA_AUDIOS, FS_ESPERADA


def gerar():
    """Cria audios/cantina_1.wav ... cantina_4.wav (senoides + ruído)."""
    fs = FS_ESPERADA
    duracao = 5.0          # segundos
    amplitude = 0.3
    nivel_ruido = 0.02
    # Conjunto de frequências (Hz) para cada um dos 4 áudios de teste.
    grupos = [[220, 1000], [440, 3000], [180, 600, 2500], [1000, 5000]]

    PASTA_AUDIOS.mkdir(exist_ok=True)
    tempo = np.linspace(0, duracao, int(fs * duracao), endpoint=False)
    for numero, frequencias in enumerate(grupos, start=1):
        sinal = np.zeros_like(tempo)
        for frequencia in frequencias:
            sinal += amplitude * np.sin(2 * np.pi * frequencia * tempo)
        sinal += nivel_ruido * np.random.randn(len(tempo))

        caminho = PASTA_AUDIOS / f"cantina_{numero}.wav"
        wavfile.write(caminho, fs, sinal.astype(np.float32))
        print(f"{caminho.name}: frequências {frequencias} Hz")

    print(f"\n4 áudios de teste gerados em: {PASTA_AUDIOS}")


if __name__ == "__main__":
    gerar()
