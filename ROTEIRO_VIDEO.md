# Roteiro do vídeo (máx. 10 min)

Regras: YouTube como **não listado**, link dentro do artigo, cada membro apresenta uma parte identificada. Gravar depois de ter os resultados finais; publicar até 29/11 e testar o link numa janela anônima em 30/11.

Ajustem a divisão conforme o número de membros (com 3 pessoas, junte os blocos 4 e 5).

| Bloco | Quem | Tempo | O que mostrar | O que dizer |
|---|---|---|---|---|
| 1. Problema e pergunta | Membro 1 | 1 min | Título do artigo; um PR real de agente no GitHub (ex.: aberto pelo Copilot) | Agentes de IA já abrem PRs sozinhos. Pergunta: o tempo até o merge deles é diferente do dos PRs humanos? H0: distribuições iguais. H1: diferentes (bilateral, porque não sabemos a direção). |
| 2. Base e método | Membro 2 | 2,5 min | Página da AIDev no Hugging Face (tag v3); trecho de limpeza do `analise.py` | Quem coletou (Li, Zhang e Hassan), como (API do GitHub), licença CC BY 4.0. VD = horas entre abertura e merge. Regras R1 a R3 e quantos PRs sobraram. Por que Mann-Whitney (tempos muito assimétricos), α = 0,05, A de Vargha-Delaney e IC por bootstrap. Estudo observacional. |
| 3. Resultado principal | Membro 3 | 3 min | Figura 1 e Tabela 1; resultado do teste | Medianas dos dois grupos, p-valor, A de Vargha-Delaney com IC e o que ele significa ("sorteando um PR de cada grupo, a chance de o do agente demorar mais é A"). Decisão sobre H0. O que isso muda na prática para quem mantém um repositório. |
| 4. Ameaças à validade | Membro 4 | 1,5 min | Seção 5 do artigo; resultado de E2 (sem merges instantâneos) | As três mais sérias: PRs de agentes são menores e mais simples; muitos são integrados pelo próprio dono; tempo até o merge não é tempo de revisão. Por isso não dá para dizer que o agente *causa* a diferença. |
| 5. Conclusão | Membro 1 ou 4 | 1 min | Seção 6 | Resposta curta à pergunta e próximo passo (controlar o tamanho do PR e medir o tempo até a primeira revisão). |
| Folga | | 1 min | | Transições e imprevistos. |

Antes de gravar, todos devem saber explicar: por que Mann-Whitney e não teste t; o que é o A de Vargha-Delaney; por que o estudo é observacional; o que as regras R1 a R3 fazem (o professor pode arguir qualquer membro).
