"""
components_v2.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gerador completo de Discord Components V2 com discord.py 2.4+
Inclui: perfil, enquete, produto, galeria, confirmação, menu, showcase
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from __future__ import annotations

import asyncio
import copy
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


def _criar_layout_view(
    componentes: list[discord.ui.Item],
    timeout: Optional[float] = 180.0,
) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView(timeout=timeout)
    for item in componentes:
        view.add_item(item)
    return view


def _copiar_callback_para_item(origem, destino) -> None:
    callback = getattr(origem, "callback", None)
    if callback is None:
        return

    # Decorated callbacks usam um wrapper interno com parent/item.
    # Copiamos o wrapper para apontar para o item real renderizado.
    if hasattr(callback, "item") and hasattr(callback, "parent"):
        try:
            callback = copy.copy(callback)
            callback.item = destino
        except Exception:
            pass

    destino.callback = callback


def _adicionar_em_action_rows(layout: discord.ui.LayoutView, itens: list[discord.ui.Item]) -> None:
    if not itens:
        return

    linha = discord.ui.ActionRow()
    largura = 0

    for item in itens:
        peso = getattr(item, "width", 1) or 1
        if peso > 5:
            peso = 5

        if largura and (largura + peso) > 5:
            layout.add_item(linha)
            linha = discord.ui.ActionRow()
            largura = 0

        linha.add_item(item)
        largura += peso

    if largura:
        layout.add_item(linha)


def _vincular_view_legado(layout: discord.ui.LayoutView, view_original: discord.ui.View) -> None:
    renderizados: dict[tuple[int, str], discord.ui.Item] = {}
    for item in layout.walk_children():
        custom_id = getattr(item, "custom_id", None)
        if not custom_id:
            continue
        if not item.is_dispatchable():
            continue
        renderizados[(item.type.value, custom_id)] = item

    faltantes: list[discord.ui.Item] = []
    for child in getattr(view_original, "children", []):
        custom_id = getattr(child, "custom_id", None)
        if not custom_id:
            continue
        if not child.is_dispatchable():
            continue

        chave = (child.type.value, custom_id)
        alvo = renderizados.get(chave)

        if alvo is None:
            try:
                faltantes.append(child.copy())
            except Exception:
                continue
            continue

        _copiar_callback_para_item(child, alvo)

    _adicionar_em_action_rows(layout, faltantes)


def _normalizar_kwargs_componentes(kwargs: dict) -> dict:
    dados = dict(kwargs)
    componentes = dados.pop("components", None)
    dados.pop("flags", None)
    if componentes is None:
        return dados

    view_original = dados.pop("view", discord.utils.MISSING)
    timeout = 180.0
    if view_original not in (None, discord.utils.MISSING):
        timeout = getattr(view_original, "timeout", 180.0)

    layout = _criar_layout_view(componentes, timeout=timeout)

    if isinstance(view_original, discord.ui.View):
        _vincular_view_legado(layout, view_original)
    elif isinstance(view_original, discord.ui.LayoutView):
        for child in getattr(view_original, "children", []):
            try:
                layout.add_item(child.copy())
            except Exception:
                continue

    dados["view"] = layout
    return dados


if not getattr(discord.InteractionResponse.send_message, "__v2_compat__", False):
    _orig_inter_send = discord.InteractionResponse.send_message
    _orig_inter_edit = discord.InteractionResponse.edit_message
    _orig_msg_send = discord.abc.Messageable.send

    async def _send_message_compat(self, content=None, **kwargs):
        kwargs = _normalizar_kwargs_componentes(kwargs)
        return await _orig_inter_send(self, content=content, **kwargs)

    async def _edit_message_compat(self, **kwargs):
        kwargs = _normalizar_kwargs_componentes(kwargs)
        return await _orig_inter_edit(self, **kwargs)

    async def _messageable_send_compat(self, content=None, **kwargs):
        kwargs = _normalizar_kwargs_componentes(kwargs)
        return await _orig_msg_send(self, content=content, **kwargs)

    _send_message_compat.__v2_compat__ = True
    discord.InteractionResponse.send_message = _send_message_compat
    discord.InteractionResponse.edit_message = _edit_message_compat
    discord.abc.Messageable.send = _messageable_send_compat

# ─────────────────────────────────────────────────────────────
#  PALETA DE CORES GLOBAL
# ─────────────────────────────────────────────────────────────

class Cores:
    AZUL    = 0x5865F2
    VERDE   = 0x57F287
    VERMELHO= 0xED4245
    AMARELO = 0xFEE75C
    ROXO    = 0x9B59B6
    LARANJA = 0xE67E22
    CIANO   = 0x1ABC9C
    CINZA   = 0x95A5A6
    BRANCO  = 0xFFFFFF
    PRETO   = 0x23272A

    MAPA: dict[str, int] = {
        "azul":     AZUL,
        "verde":    VERDE,
        "vermelho": VERMELHO,
        "amarelo":  AMARELO,
        "roxo":     ROXO,
        "laranja":  LARANJA,
        "ciano":    CIANO,
        "cinza":    CINZA,
    }

    @classmethod
    def obter(cls, nome: str) -> int:
        return cls.MAPA.get(nome.lower(), cls.AZUL)


# ─────────────────────────────────────────────────────────────
#  BUILDER UTILITÁRIO — fábricas de componentes reutilizáveis
# ─────────────────────────────────────────────────────────────

class ComponentBuilder:
    """Métodos estáticos para construir blocos V2 de forma rápida."""

    # ── Texto ────────────────────────────────────────────────

    @staticmethod
    def texto(conteudo: str) -> discord.ui.TextDisplay:
        return discord.ui.TextDisplay(conteudo)

    @staticmethod
    def titulo(texto: str, emoji: str = "") -> discord.ui.TextDisplay:
        prefixo = f"{emoji} " if emoji else ""
        return discord.ui.TextDisplay(f"# {prefixo}{texto}")

    @staticmethod
    def subtitulo(texto: str) -> discord.ui.TextDisplay:
        return discord.ui.TextDisplay(f"## {texto}")

    @staticmethod
    def negrito(texto: str) -> discord.ui.TextDisplay:
        return discord.ui.TextDisplay(f"**{texto}**")

    @staticmethod
    def campo(nome: str, valor: str, emoji: str = "•") -> discord.ui.TextDisplay:
        return discord.ui.TextDisplay(f"{emoji} **{nome}:** {valor}")

    # ── Separadores ─────────────────────────────────────────

    @staticmethod
    def separador(visivel: bool = True, tamanho: str = "small") -> discord.ui.Separator:
        espaco = (
            discord.SeparatorSpacing.large
            if tamanho == "large"
            else discord.SeparatorSpacing.small
        )
        return discord.ui.Separator(visible=visivel, spacing=espaco)

    # ── Galeria de mídia ─────────────────────────────────────

    @staticmethod
    def galeria(*urls: str) -> discord.ui.MediaGallery:
        itens = [discord.MediaGalleryItem(discord.UnfurledMediaItem(url)) for url in urls]
        return discord.ui.MediaGallery(*itens)

    @staticmethod
    def galeria_descrita(*pares: tuple[str, str]) -> discord.ui.MediaGallery:
        """Recebe pares (url, descrição)."""
        itens = [
            discord.MediaGalleryItem(
                discord.UnfurledMediaItem(url), description=descricao
            )
            for url, descricao in pares
        ]
        return discord.ui.MediaGallery(*itens)

    # ── Miniaturas (Thumbnail) ───────────────────────────────

    @staticmethod
    def miniatura(url: str, descricao: str = "") -> discord.ui.Thumbnail:
        return discord.ui.Thumbnail(
            discord.UnfurledMediaItem(url),
            description=descricao or None,
        )

    # ── Seções ───────────────────────────────────────────────

    @staticmethod
    def secao(*filhos, acessorio=None) -> discord.ui.Section:
        if acessorio is None:
            acessorio = discord.ui.Button(
                label=" ",
                style=discord.ButtonStyle.secondary,
                disabled=True,
            )
        return discord.ui.Section(*filhos, accessory=acessorio)

    # ── Botões isolados ──────────────────────────────────────

    @staticmethod
    def botao_link(label: str, url: str, emoji: str = "") -> discord.ui.Button:
        return discord.ui.Button(
            label=label,
            url=url,
            style=discord.ButtonStyle.link,
            emoji=emoji or None,
        )

    # ── Linha de ação ────────────────────────────────────────

    @staticmethod
    def linha(*componentes) -> discord.ui.ActionRow:
        return discord.ui.ActionRow(*componentes)

    # ── Container ────────────────────────────────────────────

    @staticmethod
    def container(*filhos, cor: Optional[int] = None) -> discord.ui.Container:
        return discord.ui.Container(*filhos, accent_color=cor)


# ─────────────────────────────────────────────────────────────
#  VIEW: CARTÃO DE PERFIL
# ─────────────────────────────────────────────────────────────

class PerfilView(discord.ui.View):
    def __init__(self, usuario: discord.User | discord.Member):
        super().__init__(timeout=120)
        self.usuario = usuario

    def _build(self) -> list[discord.ui.Container]:
        u = self.usuario
        avatar = str(u.display_avatar.url)

        container = ComponentBuilder.container(
            ComponentBuilder.secao(
                ComponentBuilder.titulo(u.display_name, "👤"),
                ComponentBuilder.campo("ID", str(u.id), "🆔"),
                ComponentBuilder.campo("Conta criada", discord.utils.format_dt(u.created_at, "D"), "📅"),
                acessorio=ComponentBuilder.miniatura(avatar, u.display_name),
            ),
            ComponentBuilder.separador(),
            ComponentBuilder.secao(
                ComponentBuilder.subtitulo("Estatísticas"),
                ComponentBuilder.campo("Bots", "Sim" if u.bot else "Não", "🤖"),
                ComponentBuilder.campo(
                    "Servidor",
                    u.joined_at and discord.utils.format_dt(u.joined_at, "D") or "N/A",
                    "🏠",
                )
                if isinstance(u, discord.Member)
                else ComponentBuilder.texto(""),
                acessorio=ComponentBuilder.miniatura(avatar, "Estatisticas"),
            ),
            ComponentBuilder.separador(visivel=False, tamanho="large"),
            ComponentBuilder.linha(
                ComponentBuilder.botao_link(
                    "Avatar",
                    avatar,
                    "🖼️",
                ),
            ),
            cor=Cores.AZUL,
        )
        return [container]

    @discord.ui.button(label="Atualizar", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def atualizar(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.edit_message(
            components=self._build(),
            view=self,
        )


# ─────────────────────────────────────────────────────────────
#  VIEW: ENQUETE INTERATIVA
# ─────────────────────────────────────────────────────────────

class EnqueteView(discord.ui.View):
    def __init__(self, pergunta: str, opcoes: list[str]):
        super().__init__(timeout=300)
        self.pergunta = pergunta
        self.opcoes   = opcoes[:5]          # máx 5
        self.votos: dict[str, set[int]] = {op: set() for op in self.opcoes}
        self.encerrada = False
        self._adicionar_select()

    def _adicionar_select(self):
        select = discord.ui.Select(
            placeholder="Escolha uma opção…",
            custom_id="enquete_select",
            options=[
                discord.SelectOption(label=op, value=op, emoji="🔵")
                for op in self.opcoes
            ],
        )
        select.callback = self._votar
        self.add_item(select)

    async def _votar(self, interaction: discord.Interaction):
        if self.encerrada:
            await interaction.response.send_message("❌ A enquete já foi encerrada.", ephemeral=True)
            return
        escolha = interaction.data["values"][0]
        uid     = interaction.user.id
        # Remove voto anterior
        for votos in self.votos.values():
            votos.discard(uid)
        self.votos[escolha].add(uid)
        await interaction.response.edit_message(components=self._build(), view=self)

    def _barra(self, opcao: str) -> str:
        total = sum(len(v) for v in self.votos.values())
        qtd   = len(self.votos[opcao])
        pct   = (qtd / total * 100) if total else 0
        blocos = int(pct / 10)
        return f"{'█' * blocos}{'░' * (10 - blocos)}  {pct:.0f}% ({qtd} voto{'s' if qtd != 1 else ''})"

    def _build(self) -> list[discord.ui.Container]:
        total = sum(len(v) for v in self.votos.values())
        status = "🔴 Encerrada" if self.encerrada else "🟢 Em andamento"

        linhas_resultados = [
            ComponentBuilder.texto(f"**{op}**\n{self._barra(op)}")
            for op in self.opcoes
        ]

        container = ComponentBuilder.container(
            ComponentBuilder.titulo(self.pergunta, "📊"),
            ComponentBuilder.campo("Status",       status,        "📌"),
            ComponentBuilder.campo("Total de votos", str(total),  "🗳️"),
            ComponentBuilder.separador(),
            ComponentBuilder.subtitulo("Resultados"),
            *linhas_resultados,
            ComponentBuilder.separador(visivel=False),
            ComponentBuilder.linha(
                discord.ui.Button(
                    label="Encerrar",
                    style=discord.ButtonStyle.danger,
                    custom_id="enquete_encerrar",
                    disabled=self.encerrada,
                    emoji="🛑",
                ),
            ),
            cor=Cores.ROXO,
        )
        return [container]

    @discord.ui.button(label="Encerrar", style=discord.ButtonStyle.danger,
                       custom_id="enquete_encerrar", emoji="🛑")
    async def encerrar(self, interaction: discord.Interaction, btn: discord.ui.Button):
        self.encerrada = True
        btn.disabled   = True
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                child.disabled = True
        await interaction.response.edit_message(components=self._build(), view=self)
        self.stop()


# ─────────────────────────────────────────────────────────────
#  VIEW: SHOWCASE DE PRODUTO
# ─────────────────────────────────────────────────────────────

class ProdutoView(discord.ui.View):
    def __init__(
        self,
        nome: str,
        descricao: str,
        preco: str,
        imagens: list[str],
        cor: str = "azul",
    ):
        super().__init__(timeout=180)
        self.nome      = nome
        self.descricao = descricao
        self.preco     = preco
        self.imagens   = imagens[:4]
        self.cor       = Cores.obter(cor)
        self.no_carrinho = False
        self.favorito    = False

    def _build(self) -> list[discord.ui.Container]:
        img_section = (
            ComponentBuilder.galeria(*self.imagens)
            if self.imagens
            else ComponentBuilder.texto("*(sem imagens)*")
        )

        container = ComponentBuilder.container(
            ComponentBuilder.titulo(self.nome, "🛍️"),
            img_section,
            ComponentBuilder.separador(),
            ComponentBuilder.campo("Preco", self.preco, "💰"),
            ComponentBuilder.campo("Descricao", self.descricao, "📝"),
            ComponentBuilder.campo(
                "Carrinho",
                "Adicionado ✅" if self.no_carrinho else "Vazio 🛒",
                "🛒",
            ),
            ComponentBuilder.campo(
                "Favorito",
                "Sim ❤️" if self.favorito else "Nao 🤍",
                "⭐",
            ),
            ComponentBuilder.separador(visivel=False),
            ComponentBuilder.linha(
                discord.ui.Button(
                    label="Remover do carrinho" if self.no_carrinho else "Adicionar ao carrinho",
                    style=discord.ButtonStyle.success if not self.no_carrinho else discord.ButtonStyle.secondary,
                    custom_id="prod_carrinho",
                    emoji="🛒",
                ),
                discord.ui.Button(
                    label="Desfavoritar" if self.favorito else "Favoritar",
                    style=discord.ButtonStyle.primary if not self.favorito else discord.ButtonStyle.secondary,
                    custom_id="prod_fav",
                    emoji="❤️" if not self.favorito else "🤍",
                ),
            ),
            cor=self.cor,
        )
        return [container]

    @discord.ui.button(label="Adicionar ao carrinho", style=discord.ButtonStyle.success,
                       custom_id="prod_carrinho", emoji="🛒")
    async def carrinho(self, interaction: discord.Interaction, btn: discord.ui.Button):
        self.no_carrinho = not self.no_carrinho
        await interaction.response.edit_message(components=self._build(), view=self)

    @discord.ui.button(label="Favoritar", style=discord.ButtonStyle.primary,
                       custom_id="prod_fav", emoji="❤️")
    async def favoritar(self, interaction: discord.Interaction, btn: discord.ui.Button):
        self.favorito = not self.favorito
        await interaction.response.edit_message(components=self._build(), view=self)


# ─────────────────────────────────────────────────────────────
#  VIEW: CAIXA DE CONFIRMAÇÃO
# ─────────────────────────────────────────────────────────────

class ConfirmacaoView(discord.ui.View):
    def __init__(self, acao: str, autor_id: int):
        super().__init__(timeout=60)
        self.acao     = acao
        self.autor_id = autor_id
        self.resultado: Optional[bool] = None

    def _build(self, status: str = "⏳ Aguardando confirmação…") -> list[discord.ui.Container]:
        container = ComponentBuilder.container(
            ComponentBuilder.titulo("Confirmar ação", "⚠️"),
            ComponentBuilder.campo("Ação",   self.acao, "🔧"),
            ComponentBuilder.campo("Status", status,    "📌"),
            ComponentBuilder.separador(),
            ComponentBuilder.texto("Esta ação **não pode ser desfeita**. Tem certeza?"),
            ComponentBuilder.separador(visivel=False),
            ComponentBuilder.linha(
                discord.ui.Button(
                    label="Confirmar",
                    style=discord.ButtonStyle.success,
                    custom_id="conf_sim",
                    emoji="✅",
                ),
                discord.ui.Button(
                    label="Cancelar",
                    style=discord.ButtonStyle.danger,
                    custom_id="conf_nao",
                    emoji="❌",
                ),
            ),
            cor=Cores.AMARELO,
        )
        return [container]

    async def _checar_autor(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message(
                "❌ Apenas quem iniciou pode responder.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success,
                       custom_id="conf_sim", emoji="✅")
    async def confirmar(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not await self._checar_autor(interaction):
            return
        self.resultado = True
        self._desabilitar_tudo()
        await interaction.response.edit_message(
            components=self._build("✅ Confirmado!"), view=self
        )
        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger,
                       custom_id="conf_nao", emoji="❌")
    async def cancelar(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not await self._checar_autor(interaction):
            return
        self.resultado = False
        self._desabilitar_tudo()
        await interaction.response.edit_message(
            components=self._build("❌ Cancelado."), view=self
        )
        self.stop()

    def _desabilitar_tudo(self):
        for child in self.children:
            child.disabled = True


# ─────────────────────────────────────────────────────────────
#  VIEW: MENU DE NAVEGAÇÃO
# ─────────────────────────────────────────────────────────────

PAGINAS: dict[str, dict] = {
    "inicio": {
        "titulo":   "🏠 Início",
        "descricao": "Bem-vindo ao painel principal! Selecione uma seção abaixo.",
        "campos": [
            ("Documentação", "Guias e tutoriais completos.",   "📖"),
            ("Suporte",      "Fale com nossa equipe.",         "🛠️"),
            ("Comunidade",   "Entre no nosso servidor.",       "👥"),
        ],
        "cor": Cores.AZUL,
    },
    "docs": {
        "titulo":   "📖 Documentação",
        "descricao": "Tudo que você precisa saber para começar.",
        "campos": [
            ("Instalação",   "Como instalar e configurar.",    "⚙️"),
            ("API",          "Referência completa da API.",    "🔌"),
            ("Exemplos",     "Projetos prontos para usar.",    "💡"),
        ],
        "cor": Cores.VERDE,
    },
    "suporte": {
        "titulo":   "🛠️ Suporte",
        "descricao": "Precisa de ajuda? Estamos aqui.",
        "campos": [
            ("Tickets",      "Abrir um ticket de suporte.",   "🎫"),
            ("FAQ",          "Perguntas frequentes.",          "❓"),
            ("Status",       "Estado dos servidores.",         "📡"),
        ],
        "cor": Cores.LARANJA,
    },
    "comunidade": {
        "titulo":   "👥 Comunidade",
        "descricao": "Faça parte da nossa comunidade.",
        "campos": [
            ("Discord",      "Servidor oficial.",              "💬"),
            ("GitHub",       "Repositório open-source.",       "🐙"),
            ("Blog",         "Novidades e artigos.",           "✍️"),
        ],
        "cor": Cores.ROXO,
    },
}

class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.pagina_atual = "inicio"
        self._adicionar_select()

    def _adicionar_select(self):
        select = discord.ui.Select(
            placeholder="Navegar para…",
            custom_id="menu_select",
            options=[
                discord.SelectOption(
                    label=dados["titulo"],
                    value=chave,
                    description=dados["descricao"][:50],
                )
                for chave, dados in PAGINAS.items()
            ],
        )
        select.callback = self._navegar
        self.add_item(select)

    async def _navegar(self, interaction: discord.Interaction):
        self.pagina_atual = interaction.data["values"][0]
        await interaction.response.edit_message(components=self._build(), view=self)

    def _build(self) -> list[discord.ui.Container]:
        dados = PAGINAS[self.pagina_atual]

        campos = [
            ComponentBuilder.campo(nome, valor, emoji)
            for nome, valor, emoji in dados["campos"]
        ]

        container = ComponentBuilder.container(
            ComponentBuilder.titulo(dados["titulo"]),
            ComponentBuilder.texto(dados["descricao"]),
            ComponentBuilder.separador(),
            *campos,
            ComponentBuilder.separador(visivel=False),
            ComponentBuilder.linha(
                discord.ui.Button(
                    label="← Início",
                    style=discord.ButtonStyle.secondary,
                    custom_id="menu_home",
                    disabled=self.pagina_atual == "inicio",
                    emoji="🏠",
                )
            ),
            cor=dados["cor"],
        )
        return [container]

    @discord.ui.button(label="← Início", style=discord.ButtonStyle.secondary,
                       custom_id="menu_home", emoji="🏠", disabled=True)
    async def home(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.pagina_atual = "inicio"
        await interaction.response.edit_message(components=self._build(), view=self)


# ─────────────────────────────────────────────────────────────
#  VIEW: GALERIA DE IMAGENS
# ─────────────────────────────────────────────────────────────

class GaleriaView(discord.ui.View):
    def __init__(self, titulo: str, imagens: list[tuple[str, str]]):
        """
        imagens: lista de (url, legenda)
        """
        super().__init__(timeout=180)
        self.titulo  = titulo
        self.imagens = imagens[:4]
        self.indice  = 0

    def _build(self) -> list[discord.ui.Container]:
        total = len(self.imagens)
        url, legenda = self.imagens[self.indice]

        container = ComponentBuilder.container(
            ComponentBuilder.titulo(self.titulo, "🖼️"),
            ComponentBuilder.campo("Imagem", f"{self.indice + 1} / {total}", "📷"),
            ComponentBuilder.campo("Legenda", legenda, "📝"),
            ComponentBuilder.separador(),
            ComponentBuilder.galeria_descrita((url, legenda)),
            ComponentBuilder.separador(visivel=False),
            ComponentBuilder.linha(
                discord.ui.Button(
                    label="◀ Anterior",
                    style=discord.ButtonStyle.secondary,
                    custom_id="gal_prev",
                    disabled=self.indice == 0,
                ),
                discord.ui.Button(
                    label=f"{self.indice + 1}/{total}",
                    style=discord.ButtonStyle.secondary,
                    custom_id="gal_info",
                    disabled=True,
                ),
                discord.ui.Button(
                    label="Próxima ▶",
                    style=discord.ButtonStyle.secondary,
                    custom_id="gal_next",
                    disabled=self.indice == total - 1,
                ),
            ),
            cor=Cores.CIANO,
        )
        return [container]

    @discord.ui.button(label="◀ Anterior", style=discord.ButtonStyle.secondary,
                       custom_id="gal_prev", disabled=True)
    async def anterior(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.indice = max(0, self.indice - 1)
        await interaction.response.edit_message(components=self._build(), view=self)

    @discord.ui.button(label="1/1", style=discord.ButtonStyle.secondary,
                       custom_id="gal_info", disabled=True)
    async def info(self, *_):
        pass  # Apenas indicador visual

    @discord.ui.button(label="Próxima ▶", style=discord.ButtonStyle.secondary,
                       custom_id="gal_next")
    async def proxima(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.indice = min(len(self.imagens) - 1, self.indice + 1)
        await interaction.response.edit_message(components=self._build(), view=self)


# ─────────────────────────────────────────────────────────────
#  VIEW: SHOWCASE — demonstra todos os tipos de componente
# ─────────────────────────────────────────────────────────────

def _build_mensagem_gerada(
    titulo: str,
    corpo: str,
    cor: str = "azul",
    rodape: Optional[str] = None,
    imagem_url: Optional[str] = None,
) -> list[discord.ui.Container]:
    filhos: list[discord.ui.Item] = [
        ComponentBuilder.titulo(titulo, "📝"),
        ComponentBuilder.separador(),
        ComponentBuilder.texto(corpo),
    ]

    if imagem_url:
        filhos.extend(
            [
                ComponentBuilder.separador(),
                ComponentBuilder.galeria(imagem_url),
            ]
        )

    if rodape:
        filhos.extend(
            [
                ComponentBuilder.separador(visivel=False),
                ComponentBuilder.texto(f"-# {rodape}"),
            ]
        )

    container = ComponentBuilder.container(*filhos, cor=Cores.obter(cor))
    return [container]


class GeradorMensagemModal(discord.ui.Modal):
    def __init__(self, autor_id: int, canal: Optional[discord.TextChannel] = None):
        super().__init__(title="Gerador de mensagem V2", timeout=300)
        self.autor_id = autor_id
        self.canal = canal

        self.campo_titulo = discord.ui.TextInput(
            label="Titulo",
            placeholder="Ex: Atualizacao da comunidade",
            max_length=90,
            required=True,
        )
        self.campo_corpo = discord.ui.TextInput(
            label="Corpo da mensagem",
            style=discord.TextStyle.paragraph,
            placeholder="Escreva o conteudo principal...",
            max_length=1800,
            required=True,
        )
        self.campo_rodape = discord.ui.TextInput(
            label="Rodape (opcional)",
            placeholder="Ex: Equipa de Moderacao",
            max_length=120,
            required=False,
        )
        self.campo_cor = discord.ui.TextInput(
            label="Cor (opcional)",
            placeholder="azul, verde, vermelho, amarelo, roxo, laranja, ciano, cinza",
            max_length=20,
            required=False,
            default="azul",
        )
        self.campo_imagem = discord.ui.TextInput(
            label="URL da imagem (opcional)",
            placeholder="https://...",
            max_length=500,
            required=False,
        )

        self.add_item(self.campo_titulo)
        self.add_item(self.campo_corpo)
        self.add_item(self.campo_rodape)
        self.add_item(self.campo_cor)
        self.add_item(self.campo_imagem)

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message(
                "❌ Apenas quem abriu o gerador pode enviar a mensagem.",
                ephemeral=True,
            )
            return

        titulo = self.campo_titulo.value.strip()
        corpo = self.campo_corpo.value.strip()
        rodape = self.campo_rodape.value.strip() or None
        cor_nome = (self.campo_cor.value or "azul").strip().lower() or "azul"
        imagem_url = self.campo_imagem.value.strip() or None

        if cor_nome not in Cores.MAPA:
            cores_disponiveis = ", ".join(sorted(Cores.MAPA.keys()))
            await interaction.response.send_message(
                f"❌ Cor invalida. Use uma destas: {cores_disponiveis}.",
                ephemeral=True,
            )
            return

        if imagem_url and not imagem_url.startswith(("http://", "https://")):
            await interaction.response.send_message(
                "❌ URL da imagem invalida. Use um link que comece com http:// ou https://.",
                ephemeral=True,
            )
            return

        destino = self.canal or interaction.channel
        if destino is None:
            await interaction.response.send_message(
                "❌ Nao consegui identificar o canal de destino.",
                ephemeral=True,
            )
            return

        componentes = _build_mensagem_gerada(
            titulo=titulo,
            corpo=corpo,
            cor=cor_nome,
            rodape=rodape,
            imagem_url=imagem_url,
        )

        try:
            await destino.send(components=componentes, flags=FLAGS_V2)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Sem permissao para enviar mensagens nesse canal.",
                ephemeral=True,
            )
            return
        except discord.HTTPException as erro:
            await interaction.response.send_message(
                f"❌ Falha ao enviar a mensagem: {erro}",
                ephemeral=True,
            )
            return

        local = "neste canal"
        if getattr(destino, "id", None) != interaction.channel_id:
            local = f"em {destino.mention}"
        await interaction.response.send_message(
            f"✅ Mensagem criada com sucesso {local}.",
            ephemeral=True,
        )


class GeradorMensagemView(discord.ui.View):
    def __init__(self, autor_id: int, canal: Optional[discord.TextChannel] = None):
        super().__init__(timeout=300)
        self.autor_id = autor_id
        self.canal = canal

    async def _checar_autor(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message(
                "❌ Apenas quem iniciou o gerador pode usar este painel.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Abrir formulario", style=discord.ButtonStyle.primary, emoji="🧩")
    async def abrir_formulario(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not await self._checar_autor(interaction):
            return
        await interaction.response.send_modal(
            GeradorMensagemModal(autor_id=self.autor_id, canal=self.canal)
        )


def _build_showcase() -> list[discord.ui.Container]:
    c1 = ComponentBuilder.container(
        ComponentBuilder.titulo("Components V2 — Showcase", "🧩"),
        ComponentBuilder.texto(
            "Demonstração de todos os tipos de componente disponíveis no Discord Components V2."
        ),
        cor=Cores.AZUL,
    )

    c2 = ComponentBuilder.container(
        ComponentBuilder.subtitulo("📝 TextDisplay"),
        ComponentBuilder.texto("Texto simples, **negrito**, *itálico*, `código`."),
        ComponentBuilder.campo("Campo", "Valor de exemplo", "🔹"),
        cor=Cores.VERDE,
    )

    c3 = ComponentBuilder.container(
        ComponentBuilder.subtitulo("📐 Section com acessório"),
        ComponentBuilder.secao(
            ComponentBuilder.texto("Uma seção pode ter um acessório à direita, como uma miniatura ou um botão."),
            ComponentBuilder.campo("Largura", "Flexível", "↔️"),
            acessorio=ComponentBuilder.miniatura(
                "https://cdn.discordapp.com/embed/avatars/0.png",
                "Avatar padrão",
            ),
        ),
        cor=Cores.ROXO,
    )

    c4 = ComponentBuilder.container(
        ComponentBuilder.subtitulo("🖼️ MediaGallery"),
        ComponentBuilder.galeria_descrita(
            ("https://cdn.discordapp.com/embed/avatars/0.png", "Avatar azul"),
            ("https://cdn.discordapp.com/embed/avatars/1.png", "Avatar cinza"),
        ),
        cor=Cores.LARANJA,
    )

    c5 = ComponentBuilder.container(
        ComponentBuilder.subtitulo("━ Separadores"),
        ComponentBuilder.texto("Separador visível abaixo:"),
        ComponentBuilder.separador(visivel=True, tamanho="small"),
        ComponentBuilder.texto("Separador grande e invisível abaixo:"),
        ComponentBuilder.separador(visivel=False, tamanho="large"),
        ComponentBuilder.texto("Fim dos separadores."),
        cor=Cores.CINZA,
    )

    c6 = ComponentBuilder.container(
        ComponentBuilder.subtitulo("🎛️ ActionRow — Botões e Select"),
        ComponentBuilder.texto("Linha de botões:"),
        ComponentBuilder.linha(
            discord.ui.Button(label="Primário",   style=discord.ButtonStyle.primary,   custom_id="sc_p",  emoji="🔵"),
            discord.ui.Button(label="Sucesso",    style=discord.ButtonStyle.success,   custom_id="sc_s",  emoji="🟢"),
            discord.ui.Button(label="Perigo",     style=discord.ButtonStyle.danger,    custom_id="sc_d",  emoji="🔴"),
            discord.ui.Button(label="Secundário", style=discord.ButtonStyle.secondary, custom_id="sc_sec",emoji="⚪"),
        ),
        ComponentBuilder.separador(visivel=False),
        ComponentBuilder.texto("Select menu:"),
        ComponentBuilder.linha(
            discord.ui.Select(
                placeholder="Selecione uma opção…",
                custom_id="sc_sel",
                options=[
                    discord.SelectOption(label="Opção A", value="a", emoji="🅰️"),
                    discord.SelectOption(label="Opção B", value="b", emoji="🅱️"),
                    discord.SelectOption(label="Opção C", value="c", emoji="🅾️"),
                ],
            )
        ),
        cor=Cores.CIANO,
    )

    return [c1, c2, c3, c4, c5, c6]


# ─────────────────────────────────────────────────────────────
#  COG PRINCIPAL
# ─────────────────────────────────────────────────────────────

try:
    FLAGS_V2 = discord.MessageFlags(components_v2=True)
except TypeError:
    # Compatibilidade com builds antigas/forks que usam o nome anterior.
    FLAGS_V2 = discord.MessageFlags(is_components_v2=True)

class ComponentsV2Cog(commands.Cog, name="ComponentsV2"):
    """Gerador completo de Discord Components V2."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── /v2_perfil ──────────────────────────────────────────

    @app_commands.command(name="v2perfil", description="Exibe um cartão de perfil com Components V2.")
    @app_commands.describe(usuario="Usuário alvo (padrão: você mesmo)")
    async def v2_perfil(
        self,
        interaction: discord.Interaction,
        usuario: Optional[discord.User] = None,
    ):
        alvo = usuario or interaction.user
        view = PerfilView(alvo)
        await interaction.response.send_message(
            components=view._build(),
            view=view,
            flags=FLAGS_V2,
        )

    # ── /v2_enquete ─────────────────────────────────────────

    @app_commands.command(name="v2enquete", description="Cria uma enquete interativa com Components V2.")
    @app_commands.describe(
        pergunta="Pergunta da enquete",
        opcao1="Opção 1",
        opcao2="Opção 2",
        opcao3="Opção 3 (opcional)",
        opcao4="Opção 4 (opcional)",
        opcao5="Opção 5 (opcional)",
    )
    async def v2_enquete(
        self,
        interaction: discord.Interaction,
        pergunta: str,
        opcao1: str,
        opcao2: str,
        opcao3: Optional[str] = None,
        opcao4: Optional[str] = None,
        opcao5: Optional[str] = None,
    ):
        opcoes = [op for op in [opcao1, opcao2, opcao3, opcao4, opcao5] if op]
        if len(opcoes) < 2:
            await interaction.response.send_message("❌ São necessárias pelo menos 2 opções.", ephemeral=True)
            return
        view = EnqueteView(pergunta, opcoes)
        await interaction.response.send_message(
            components=view._build(),
            view=view,
            flags=FLAGS_V2,
        )

    # ── /v2_produto ─────────────────────────────────────────

    @app_commands.command(name="v2produto", description="Cria um showcase de produto com Components V2.")
    @app_commands.describe(
        nome="Nome do produto",
        descricao="Descrição do produto",
        preco="Preço (ex: R$ 99,90)",
        imagem1="URL da imagem 1",
        imagem2="URL da imagem 2 (opcional)",
        cor="Cor do container: azul, verde, vermelho, amarelo, roxo, laranja, ciano",
    )
    async def v2_produto(
        self,
        interaction: discord.Interaction,
        nome: str,
        descricao: str,
        preco: str,
        imagem1: str,
        imagem2: Optional[str] = None,
        cor: str = "azul",
    ):
        imagens = [img for img in [imagem1, imagem2] if img]
        view = ProdutoView(nome, descricao, preco, imagens, cor)
        await interaction.response.send_message(
            components=view._build(),
            view=view,
            flags=FLAGS_V2,
        )

    # ── /v2_confirmar ───────────────────────────────────────

    @app_commands.command(name="v2confirmar", description="Exibe uma caixa de confirmação com Components V2.")
    @app_commands.describe(acao="Descrição da ação a confirmar")
    async def v2_confirmar(self, interaction: discord.Interaction, acao: str):
        view = ConfirmacaoView(acao, interaction.user.id)
        await interaction.response.send_message(
            components=view._build(),
            view=view,
            flags=FLAGS_V2,
        )

        try:
            await asyncio.wait_for(view.wait(), timeout=60)
        except asyncio.TimeoutError:
            pass

        if view.resultado is True:
            await interaction.followup.send(f"✅ Ação **{acao}** confirmada.", ephemeral=True)
        elif view.resultado is False:
            await interaction.followup.send(f"❌ Ação **{acao}** cancelada.", ephemeral=True)
        else:
            await interaction.followup.send("⏰ Tempo esgotado.", ephemeral=True)

    # ── /v2_menu ─────────────────────────────────────────────

    @app_commands.command(name="v2menu", description="Exibe um menu de navegação com Components V2.")
    async def v2_menu(self, interaction: discord.Interaction):
        view = MenuView()
        await interaction.response.send_message(
            components=view._build(),
            view=view,
            flags=FLAGS_V2,
        )

    # ── /v2_galeria ──────────────────────────────────────────

    @app_commands.command(name="v2galeria", description="Cria uma galeria navegável com Components V2.")
    @app_commands.describe(
        titulo="Título da galeria",
        url1="URL da imagem 1",
        legenda1="Legenda da imagem 1",
        url2="URL da imagem 2 (opcional)",
        legenda2="Legenda da imagem 2",
        url3="URL da imagem 3 (opcional)",
        legenda3="Legenda da imagem 3",
    )
    async def v2_galeria(
        self,
        interaction: discord.Interaction,
        titulo: str,
        url1: str,
        legenda1: str = "Imagem 1",
        url2: Optional[str] = None,
        legenda2: str = "Imagem 2",
        url3: Optional[str] = None,
        legenda3: str = "Imagem 3",
    ):
        pares = [(url1, legenda1)]
        if url2:
            pares.append((url2, legenda2))
        if url3:
            pares.append((url3, legenda3))

        view = GaleriaView(titulo, pares)
        await interaction.response.send_message(
            components=view._build(),
            view=view,
            flags=FLAGS_V2,
        )

    # ── /v2_showcase ─────────────────────────────────────────

    @app_commands.command(name="v2showcase", description="Demonstra todos os tipos de Components V2.")
    async def v2_showcase(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            components=_build_showcase(),
            flags=FLAGS_V2,
        )

    # ── /v2_builder ──────────────────────────────────────────

    @app_commands.command(name="v2builder", description="Cria um container personalizado via prompt livre.")
    @app_commands.describe(
        titulo="Título principal",
        corpo="Corpo do texto (suporta markdown)",
        rodape="Texto de rodapé",
        cor="Cor: azul, verde, vermelho, amarelo, roxo, laranja, ciano, cinza",
    )
    async def v2_builder(
        self,
        interaction: discord.Interaction,
        titulo: str,
        corpo: str,
        rodape: Optional[str] = None,
        cor: str = "azul",
    ):
        filhos = [
            ComponentBuilder.titulo(titulo),
            ComponentBuilder.separador(),
            ComponentBuilder.texto(corpo),
        ]
        if rodape:
            filhos += [
                ComponentBuilder.separador(visivel=False),
                ComponentBuilder.texto(f"-# {rodape}"),
            ]

        container = ComponentBuilder.container(*filhos, cor=Cores.obter(cor))
        await interaction.response.send_message(
            components=[container],
            flags=FLAGS_V2,
        )

    # ── Prefixed aliases ─────────────────────────────────────

    @app_commands.command(name="v2mensagem", description="Abre um gerador de mensagens com Components V2.")
    @app_commands.describe(canal="Canal de destino (opcional)")
    async def v2_mensagem(
        self,
        interaction: discord.Interaction,
        canal: Optional[discord.TextChannel] = None,
    ):
        view = GeradorMensagemView(autor_id=interaction.user.id, canal=canal)
        destino = canal.mention if canal else "este canal"
        await interaction.response.send_message(
            f"🧩 Gerador pronto. Clique no botao abaixo para criar e enviar a mensagem em {destino}.",
            view=view,
            ephemeral=True,
        )

    @commands.command(name="v2showcase")
    async def v2_showcase_prefix(self, ctx: commands.Context):
        """Versão com prefixo de !v2_showcase."""
        await ctx.send(components=_build_showcase(), flags=FLAGS_V2)

    @commands.command(name="v2builder")
    async def v2_builder_prefix(self, ctx: commands.Context, cor: str = "azul", *, texto: str):
        """Versão com prefixo: !v2_builder [cor] <texto>"""
        container = ComponentBuilder.container(
            ComponentBuilder.titulo("Mensagem Personalizada", "✨"),
            ComponentBuilder.separador(),
            ComponentBuilder.texto(texto),
            cor=Cores.obter(cor),
        )
        await ctx.send(components=[container], flags=FLAGS_V2)


# ─────────────────────────────────────────────────────────────
    @commands.command(name="v2mensagem")
    async def v2_mensagem_prefix(self, ctx: commands.Context, cor: str = "azul", *, texto: str):
        """Versao rapida: !v2mensagem [cor] <texto>"""
        componentes = _build_mensagem_gerada(
            titulo="Mensagem",
            corpo=texto,
            cor=cor,
        )
        await ctx.send(components=componentes, flags=FLAGS_V2)

#  SETUP
# ─────────────────────────────────────────────────────────────

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ComponentsV2Cog(bot))
