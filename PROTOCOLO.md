# Protocolo do Projeto Final (MCEQ 12576)

Registrado antes da análise dos dados. Data do registro: ____/____/2026.

| Campo | Conteúdo |
|---|---|
| **EQUIPE / MEMBROS** | William Kenzo Nakao; [membro 2]; [membro 3]; [membro 4] |
| **PROBLEMA (lacuna)** | Agentes de IA generativa já abrem pull requests (PRs) sozinhos em projetos open source, mas não se sabe se esses PRs passam pela revisão e são integrados mais rápido ou mais devagar que os PRs escritos por humanos nos mesmos projetos. |
| **PERGUNTA DE PESQUISA** | Em repositórios open source populares do GitHub, PRs abertos por agentes autônomos de IA têm tempo até o merge diferente do tempo de PRs abertos por desenvolvedores humanos? |
| **H0** | Med(agente) = Med(humano): a distribuição do tempo até o merge é a mesma nos dois grupos (P(X > Y) = P(X < Y)). |
| **H1** | [ ] unilateral [X] bilateral. Med(agente) ≠ Med(humano): as distribuições diferem (P(X > Y) ≠ P(X < Y)). |
| **VI (fator) e níveis** | Autoria do PR: (1) agente autônomo de IA (OpenAI Codex, Devin, GitHub Copilot, Cursor, Claude Code); (2) desenvolvedor humano. |
| **VD e unidade** | Tempo entre a abertura do PR e o merge, em horas. |
| **CONTROLE / MODERADORA** | Controle: só repositórios que têm PRs dos dois grupos; só PRs integrados (merged). Moderadora (exploratória): repositório (blocos). |
| **O QUE MUDOU EM RELAÇÃO À FICHA** | (1) VI: "uso de assistente de IA na escrita" virou "PR aberto por agente autônomo de IA × PR humano", porque a base pública identifica a autoria do agente, não o uso de assistente pelo humano. (2) VD: "tempo de revisão em minutos" virou "tempo até o merge em horas", porque a base tem os carimbos de abertura e merge de todos os PRs, mas não tem dados de revisão para os PRs humanos. (3) H1 passou de unilateral para bilateral: a literatura não indica com segurança a direção do efeito. (4) O contexto "equipes de médio porte" virou "repositórios open source populares". |
| **BASE ESCOLHIDA** | AIDev, versão v3 (MSR 2026 Mining Challenge), Hugging Face `hao-li/AIDev`, tag `v3`. Tabelas `pull_request` (PRs de agentes em repositórios com mais de 100 estrelas) e `human_pull_request` (PRs humanos amostrados dos mesmos repositórios, com mais de 500 estrelas). Licença CC BY 4.0. Artigo de origem: Li, Zhang e Hassan (2025), arXiv:2507.15003. Data de acesso: ____/____/2026. |
| **JUSTIFICATIVA DA BASE** | Proveniência: grupo SAIL (Queen's University), artigo associado e versão fixa (tag v3). Documentação: dicionário de colunas (`data_table.md`). Licença: CC BY 4.0 permite uso acadêmico e redistribuição. Tamanho: milhares de PRs por grupo. Variáveis: VI e VD existem ou são derivadas de forma direta. Medição: carimbos de data e hora da API do GitHub. |
| **TIPO DE ESTUDO** | [ ] experimento publicado [X] observacional (sem afirmações causais) |
| **DESENHO** | [X] 2 grupos independentes [ ] pareado [ ] blocos [ ] k tratamentos |
| **UNIDADE DE ANÁLISE e n** | Um PR integrado. n por grupo é conhecido só depois da limpeza (registrado no README). |
| **REGRAS DE LIMPEZA** | R1: manter só PRs com `merged_at`. R2: excluir tempos ausentes ou negativos. R3: manter só repositórios com PRs dos dois grupos. Nenhuma outra exclusão. |
| **TESTE PREVISTO, α e estatística** | Mann-Whitney U, bilateral, α = 0,05. Motivo: tempos até o merge são muito assimétricos (cauda longa à direita), então o teste t não é adequado. |
| **TESTE ALTERNATIVO** | Não se aplica (o teste já é não paramétrico). Verificação de robustez: Welch sobre log(horas + 1/60), relatada como exploratória se feita. |
| **TAMANHO DE EFEITO E IC** | A de Vargha-Delaney, A = P(X > Y) (limiares 0,56 / 0,64 / 0,71; Vargha e Delaney, 2000), e diferença das medianas, ambos com IC 95% por bootstrap (2000 reamostragens, semente 2026). Na análise por blocos (E1), r bisserial (Kerby, 2014). Convenção da Aula 08. |
| **ANÁLISES EXPLORATÓRIAS PREVISTAS** | E1: Wilcoxon pareado com o repositório como bloco (mediana do agente × mediana humana por repositório), com r bisserial. E2: repetir o teste principal sem merges em menos de 1 minuto. E3: descritiva por agente. |
| **AMEAÇAS À VALIDADE INICIAIS** | Conclusão: n grande torna diferenças pequenas "significativas" (por isso o tamanho de efeito). Interna: confundimento por tipo e tamanho da tarefa, período diferente de coleta dos grupos, merges automáticos pelo próprio dono. Construção: tempo até o merge não é tempo de revisão; PRs "humanos" podem ter usado IA sem declarar. Externa: só repositórios populares do GitHub e só PRs integrados. |
