# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Idioma

Este é um trabalho acadêmico em português (disciplina Análise e Processamento de Sinais). Escreva código, comentários, nomes de variáveis, títulos de gráficos e respostas em português.

## Estado atual

O projeto ainda não foi iniciado. Por enquanto só existe `Instruções.txt` com o enunciado do professor e as instruções do aluno. Não há código, dependências nem testes definidos — esta seção deve ser atualizada conforme o projeto evoluir.

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

- Python com biblioteca de áudio para a aquisição.
- Processamento e análise espectral (FFT, filtros) e visualização dos resultados.

Escolha as bibliotecas conforme a necessidade ao implementar; ao adicioná-las, documente aqui o comando de instalação e como executar os scripts.

## Convenções de código (definidas pelo aluno)

Seguir estritamente estas regras ao escrever o código:
- Dentro de cada função, **declarar as constantes primeiro**, com nomes simples.
- Estruturar a lógica priorizando a clareza para explicar o código (o código será apresentado e explicado).
- Manter o código simples, organizado e de fácil manutenção — evitar abstrações e complexidade desnecessárias.
