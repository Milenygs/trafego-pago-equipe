# Instalação no seu computador

Este repositório tem as skills de tráfego que usamos com o Claude Code. Você recebe as
atualizações, mas quem altera as skills é sempre a Mileny.

Tempo: uns 30 minutos. Faça na ordem.

## 1. Instalar os programas

| Programa | Onde baixar | Atenção |
|---|---|---|
| Git | git-scm.com/download/win | Pode aceitar todas as opções padrão |
| Python 3.12 ou mais novo | python.org/downloads | Na primeira tela, marque **"Add python.exe to PATH"** |
| Claude Code | claude.ai/download | Entre com a sua conta Claude |
| OneDrive | já vem no Windows | Entre com o seu Hotmail. A pasta **Carteira** precisa aparecer em `OneDrive\Carteira` |

## 2. Aceitar o convite do GitHub

Abra o e-mail do GitHub e clique em **"Accept invitation"**.

## 3. Baixar as skills

Abra o **PowerShell** (menu Iniciar → digite "PowerShell") e cole um bloco por vez:

```powershell
New-Item -ItemType Directory -Force "$HOME\OneDrive\.claude" | Out-Null
git clone https://github.com/Milenygs/trafego-equipe.git "$HOME\OneDrive\.claude\skills"
```

Na primeira vez, o Git abre uma janela para você entrar na sua conta do GitHub.

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\commands" | Out-Null
if (Test-Path "$HOME\.claude\skills") { Remove-Item "$HOME\.claude\skills" -Recurse }
New-Item -ItemType Junction -Path "$HOME\.claude\skills" -Target "$HOME\OneDrive\.claude\skills"
Copy-Item "$HOME\.claude\skills\_comandos\*.md" "$HOME\.claude\commands\"
pip install facebook-business requests pyyaml openpyxl
```

> Se a pasta do seu OneDrive tiver outro nome (por exemplo "OneDrive - Pessoal"), me
> avise antes de continuar: as skills procuram `OneDrive\Carteira` e `OneDrive\.claude`.

## 4. Acesso às contas de anúncio

**Você não recebe o token da Mileny.** Ela cria um acesso só seu no Business Manager e
configura o arquivo `.env` no seu computador junto com você. Até lá, as skills funcionam para
ler e estudar, mas não conseguem puxar dados da Meta.

## 5. Atualizar

Sempre que a Mileny avisar que mudou alguma skill, abra o Claude Code e digite:

```
/atualizar-skills
```

## Regras

- Não edite as skills. Se achar algo errado, fale com a Mileny.
- Campanha, conjunto e anúncio novos sobem **pausados**. Quem ativa é a Mileny.
- Nada é aplicado nas contas sem o ok da Mileny.
- Na pasta Carteira, registre no `decisoes.md` e no `historico\` só o que a Mileny aprovou.
  Não apague nem mova arquivos: o que muda aí muda no computador dela também.
