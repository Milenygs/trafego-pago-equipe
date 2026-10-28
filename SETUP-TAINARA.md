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
git clone https://github.com/Milenygs/trafego-pago-equipe.git "$HOME\OneDrive\.claude\skills"
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

## Registro das ações (desde 28/10/2026)

Tudo o que nós duas fazemos nas contas fica registrado **na `OneDrive\Carteira`**, para as duas verem.

- **Abra o Claude Code sempre dentro de `OneDrive\Carteira`** (ou da pasta do cliente). Nunca
  trabalhe na cópia `02-carteira-clientes-meta` do pacote em zip: ela é antiga e não sincroniza.
  Se ainda tiver essa cópia no seu computador, pode apagar.
- **Mexeu pelo Claude:** ele registra na hora no `historico\` e no `decisoes.md` do cliente.
- **Mexeu direto no Gerenciador:** às 7h do dia seguinte o registro automático grava a mudança no
  `historico\` do cliente, com o seu nome e o horário, e "Motivo: a preencher". Abra o Claude na
  Carteira e diga: *"registra: pausei a campanha X da Facilmart porque Y"*. Ele completa a linha.
  O Extrato da manhã lista as mudanças que ainda estão sem motivo.
- **Relatório da manhã:** não gere o extrato no seu computador. O do dia fica em
  `OneDrive\Carteira\_Central\extrato\extrato-AAAA-MM-DD.html`. Abra pelo navegador.
