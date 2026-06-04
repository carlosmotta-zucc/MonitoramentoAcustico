# Processa os WAVs de audios/: tempo, FFT, espectrograma, filtros e nível
# comparado à NBR 10151. Rodar da pasta codigo/:  python main.py

import numpy as np

import processamento as proc


# Imprime a tabela comparativa dos níveis entre as medições.
def imprimir_tabela(nomes, niveis, situacoes):
    largura = 48
    print("\n" + "=" * largura)
    print("NÍVEIS DE RUÍDO vs NBR 10151 (limite diurno 50 dB(A))")
    print("=" * largura)
    print(f"{'Arquivo':<24}{'dB':<10}{'Situação'}")
    print("-" * largura)
    for nome, nivel, situacao in zip(nomes, niveis, situacoes):
        print(f"{nome:<24}{nivel:<10.1f}{situacao}")
    print("=" * largura)


def main():
    proc.PASTA_RESULTADOS.mkdir(exist_ok=True)
    audios = proc.listar_audios()
    if not audios:
        print("Nenhum .wav encontrado em audios/.")
        print("Coloque os arquivos na pasta audios/ e rode novamente.")
        return

    print(f"Processando {len(audios)} áudio(s)...\n")
    nomes, niveis, situacoes = [], [], []

    for caminho in audios:
        base = caminho.stem
        sinal, fs = proc.carregar(caminho)

        # Tempo
        rms = np.sqrt(np.mean(sinal ** 2))
        pico = np.max(np.abs(sinal))
        proc.plot_forma_onda(sinal, fs,
                             f"Forma de onda — {base}", f"{base}_onda.png")

        # Frequência (FFT + picos)
        frequencias, amplitudes = proc.espectro(sinal, fs)
        picos = proc.picos_predominantes(frequencias, amplitudes)
        proc.plot_espectro(frequencias, amplitudes, picos,
                          f"Espectro — {base}", f"{base}_espectro.png")

        # Espectrograma
        f_esp, t_esp, energia = proc.espectrograma(sinal, fs)
        proc.plot_espectrograma(f_esp, t_esp, energia,
                              f"Espectrograma — {base}", f"{base}_espectrograma.png")

        # Filtros FIR e IIR (resposta dos dois + sinal filtrado pelo IIR)
        b_iir, a_iir = proc.projetar_iir(fs)
        b_fir, a_fir = proc.projetar_fir(fs)
        curvas = [("FIR", *proc.resposta_frequencia(b_fir, a_fir, fs)),
                  ("IIR", *proc.resposta_frequencia(b_iir, a_iir, fs))]
        proc.plot_resposta_filtros(curvas,
                                 f"Resposta dos filtros — {base}", f"{base}_filtros.png")
        sinal_filtrado = proc.aplicar_filtro(sinal, b_iir, a_iir)
        proc.plot_forma_onda(sinal_filtrado, fs,
                            f"Forma de onda filtrada (IIR) — {base}",
                            f"{base}_onda_filtrada.png")

        # Nível e norma
        nivel = proc.nivel_db(sinal)
        limite, situacao = proc.comparar_norma(nivel)

        nomes.append(base)
        niveis.append(nivel)
        situacoes.append(situacao)

        picos_txt = ", ".join(f"{f:.0f} Hz" for f, _ in picos) or "(nenhum)"
        print(f"-> {base}")
        print(f"   RMS={rms:.3f}  pico={pico:.3f}")
        print(f"   picos predominantes: {picos_txt}")
        print(f"   nível: {nivel:.1f} dB -> {situacao} do limite {limite}\n")

    # Painel comparativo final (material de divulgação)
    proc.plot_comparacao_niveis(nomes, niveis, "comparacao_niveis.png")
    imprimir_tabela(nomes, niveis, situacoes)
    print(f"\nFiguras salvas em: {proc.PASTA_RESULTADOS}")


if __name__ == "__main__":
    main()
