---
description: Atualiza as skills de tráfego com a versão mais recente enviada pela Mileny
---

Atualize as skills da equipe de tráfego e responda em português simples.

1. Rode no terminal: `git -C "$HOME/.claude/skills" pull --ff-only`
2. Copie os comandos novos: `Copy-Item "$HOME\.claude\skills\_comandos\*.md" "$HOME\.claude\commands\" -Force`
3. Responda em 1 ou 2 linhas quais skills mudaram (ou "já estava tudo atualizado").

Se o pull falhar porque algum arquivo foi alterado neste computador, **não force nem apague nada**.
Explique em linguagem simples qual arquivo foi alterado e oriente a falar com a Mileny: as skills
só são editadas por ela.
