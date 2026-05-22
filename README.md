# Gerador de Componentes V2

Bot Discord com `discord.py` para criar mensagens com Components V2 (containers, texto, galeria, seções, botões e menus).

## Requisitos

- Python 3.11+
- `discord.py 2.7+`

## Instalação

1. Instala dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Cria o ficheiro `.env` com:
   ```env
   DISCORD_TOKEN=seu_token_aqui
   ```
3. Inicia o bot:
   ```bash
   python main.py
   ```

## Cores Aceites

- `azul`
- `verde`
- `vermelho`
- `amarelo`
- `roxo`
- `laranja`
- `ciano`
- `cinza`

## Comandos Slash

### `/v2perfil`
Mostra um cartão de perfil.

Parâmetros:
- `usuario` (opcional): utilizador alvo.

Como funciona:
- Renderiza dados do utilizador (ID, criação da conta, entrada no servidor quando aplicável).
- Inclui botão de atualização.

### `/v2enquete`
Cria uma enquete com votação por select.

Parâmetros:
- `pergunta`
- `opcao1`
- `opcao2`
- `opcao3` (opcional)
- `opcao4` (opcional)
- `opcao5` (opcional)

Como funciona:
- Cada utilizador pode trocar o próprio voto.
- Mostra barra de progresso por opção.
- Botão para encerrar a enquete.

### `/v2produto`
Cria um showcase de produto.

Parâmetros:
- `nome`
- `descricao`
- `preco`
- `imagem1`
- `imagem2` (opcional)
- `cor` (opcional, padrão: `azul`)

Como funciona:
- Exibe detalhes e imagens do produto.
- Botões para carrinho e favorito.

### `/v2confirmar`
Abre uma caixa de confirmação.

Parâmetros:
- `acao`

Como funciona:
- Apenas o autor do comando pode confirmar/cancelar.
- Retorna resultado por mensagem efémera.

### `/v2menu`
Abre um painel de navegação.

Como funciona:
- Select para navegar entre páginas.
- Botão para voltar ao início.

### `/v2galeria`
Cria uma galeria navegável.

Parâmetros:
- `titulo`
- `url1`
- `legenda1` (opcional, padrão: `Imagem 1`)
- `url2` (opcional)
- `legenda2` (opcional, padrão: `Imagem 2`)
- `url3` (opcional)
- `legenda3` (opcional, padrão: `Imagem 3`)

Como funciona:
- Botões anterior/próxima para trocar imagem.
- Mostra posição atual.

### `/v2showcase`
Mostra uma demonstração completa dos tipos de Components V2 usados no projeto.

### `/v2builder`
Cria um container personalizado por texto.

Parâmetros:
- `titulo`
- `corpo`
- `rodape` (opcional)
- `cor` (opcional, padrão: `azul`)

Como funciona:
- Gera mensagem rápida com título, corpo e rodapé.

### `/v2mensagem`
Abre um gerador por formulário (modal).

Parâmetros:
- `canal` (opcional): canal de destino.

Como funciona:
- Mostra botão para abrir formulário.
- O formulário aceita: título, corpo, rodapé, cor e URL de imagem.
- Valida cor e URL antes de enviar.

## Comandos de Prefixo

### `!v2showcase`
Envia a demonstração completa.

### `!v2builder [cor] <texto>`
Envia uma mensagem personalizada simples.

### `!v2mensagem [cor] <texto>`
Envia uma mensagem rápida usando o gerador base.

## Notas Técnicas

- O projeto está adaptado para `discord.py 2.7+`, convertendo payloads `components=` para `LayoutView` automaticamente.
- Isso mantém compatibilidade com os comandos já escritos no estilo V2 deste repositório.
