# Tempo até o merge: PRs de agentes de IA × PRs humanos

Projeto Final de MCEQ 12576 (PUC-Campinas, 2º semestre de 2026).

## Pergunta

Em repositórios open source populares do GitHub, PRs abertos por agentes autônomos de IA têm tempo até o merge diferente do tempo de PRs abertos por humanos?

- H0: as distribuições do tempo até o merge são iguais nos dois grupos.
- H1 (bilateral): as distribuições diferem.
- Estudo **observacional**: os resultados indicam associação, não causa.

O plano completo, registrado antes da análise, está em [`PROTOCOLO.md`](PROTOCOLO.md).

## Dados

- **Base:** AIDev v3 (Li, Zhang e Hassan, 2025), https://huggingface.co/datasets/hao-li/AIDev/tree/v3
- **Artigo de origem:** arXiv:2507.15003
- **Tabelas usadas:** `pull_request` (PRs de agentes, repositórios com mais de 100 estrelas) e `human_pull_request` (PRs humanos dos mesmos repositórios, com mais de 500 estrelas)
- **Licença:** CC BY 4.0
- **Data de acesso:** ____/____/2026

O script baixa os arquivos brutos direto do Hugging Face (versão fixa `v3`), então eles não ficam neste repositório. A pasta `dados/limpos/` é gerada pelo script.

## Como reexecutar

No Google Colab, abra `analise.ipynb` e rode todas as células. Ou, localmente:

```bash
pip install -r requirements.txt
python analise.py
```

Leva poucos minutos (download de ~20 MB + 2000 reamostragens de bootstrap). A semente é fixa (`2026`), então os números saem iguais a cada execução.

## O que o script gera

| Arquivo | Conteúdo |
|---|---|
| `dados/limpos/prs_merged.csv` | PRs integrados depois da limpeza (regras R1 a R3 do protocolo) |
| `resultados/tabela_descritiva.csv` | n, média, DP, quartis, P90 e % de merges em menos de 1 min, por grupo |
| `resultados/tabela_descritiva_por_agente.csv` | A mesma tabela, por agente |
| `resultados/resultados.json` | Contagens da limpeza, teste principal, efeito, ICs e análises exploratórias |
| `figuras/fig1_tempo_merge.png` / `.pdf` | Boxplot do tempo até o merge (escala log) |

## Análises

- **Confirmatória:** Mann-Whitney U bilateral, α = 0,05; A de Vargha-Delaney e diferença das medianas com IC 95% por bootstrap.
- **Exploratórias** (fora do protocolo confirmatório): E1, Wilcoxon pareado com o repositório como bloco (r bisserial); E2, teste principal sem merges em menos de 1 minuto; E3, descritiva por agente.

## Estrutura

```
analise.py          script principal (dados brutos -> números e figura do artigo)
analise.ipynb       o mesmo, para rodar no Colab
PROTOCOLO.md        protocolo de 1 página
requirements.txt
dados/limpos/       gerado pelo script
resultados/         gerado pelo script
figuras/            gerado pelo script
```
