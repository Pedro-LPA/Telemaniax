#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import subprocess
import os
import sys
import uuid
import random
import time

from rich.console import Console
from rich.theme import Theme

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

custom_theme = Theme({
    "neon": "bold green",
})

console = Console(theme=custom_theme)

APP_NAME = "TELEMANIAX"
VERSION = "1.0.0"

M3U_FILES = [
    "novalista.m3u8",
    "CanaisBR01.m3u8",
    "CanaisBR02.m3u8",
    "CanaisBR03.m3u8",
    "CanaisBR04.m3u8",
    "CanaisBR05.m3u8",
    "CanaisIPTV.m3u"
]

CANAIS_IGNORADOS = {
    "1001 Noites", "AgroBrasil TV", "Alpha Channel", "Amazon Sat", "Angel TV Portuguese",
    "AWTV", "BDC TV", "Canal 38", "Canal do Criador", "Canal Educação", "Canal Rural",
    "Canal Saúde", "Catve2", "Catve FM", "Catve Master TV", "Classique TV", "Gospel Movie TV",
    "KpopTV Play", "Kuriakos Kids", "MKK Web TV", "MyTime Movie Network Brazil", "Nova Era TV",
    "Novo Tempo", "Plena TV", "Primer TV", "Rede TV! SP", "RIT TV", "Santa Cecilia TV", "SBT Interior",
    "SESC TV", "STZ TV", "TCM 10 HD", "TV Aldeia", "TV Aliança Catarinense", "TV Alternativa",
    "TV Aparecida", "TV Assembléia Ceará", "TV Birigui", "TV Cidade de Petrópolis",
    "TV Cidade Oeste", "TV Cidade Verde", "TV Cidade Verde Cuiaba", "TV Curuça", "TV das Artes",
    "TV Destak", "TV Diário Macapá", "TV Difusora Leste", "TV Digital Biriguí", "TV do Povo",
    "TV Empire Magazine", "TV Encontro das Aguas", "TV Evangelizar", "TV Futuro", "TV Gideoes",
    "TV Grao Pará", "TV Interlagos", "TV Liberdade", "TV Mackenzie", "TV Mais Maricá",
    "TV Maná Brasil", "TV Marajoara", "TV MAX", "TV Modelo", "TV Padre Cicero", "TV Paraense",
    "TV Paraná Turismo", "TV Passo Fundo", "TV Sandegi", "TV São Raimundo", "TV Sim Cachoeiro",
    "TV Sim Colatina", "TV Sim São Mateus", "TV Sol Comunidade", "TV Sul de Minas",
    "TV Terceiro Anjo", "TV Thathi", "TV UFG", "TV Universal", "TV Viçosa", "TV Vila Real",
    "TV Zoom", "TVC-Rio", "TVCOM DF", "TVCOM Maceió", "TVídeoNews", "TVitapé", "TVMatic Comedy",
    "TVMatic Crafts", "TVMatic Facebook", "TVMatic Fight", "TVMatic Funny", "TVMatic TikTok",
    "TVNBN", "UNISUL TV", "UniTV Porto Alegre", "VRT Channel", "VV8 TV",
    "Boas Novas", "Cabo Frio TV", "Canal 25 Jundiaí", "Canal do Inter", "Canal Libras",
    "Canal Ricos", "Combate Global", "Conecta+ TV", "Conexão TV", "Elemental Channel",
    "ElyTV", "Ghost TV", "Gloob", "ISTV", "Play TV", "RBATV", "Rede Gospel", "Rede Minas",
    "Rede RC", "SIC TV", "Times Brasil", "TV BRICS Portuguese", "TV Câmara 2", "TV Grande Natal",
    "TV Life America", "Record TV Brasilia", "Record TV Itapoan", "Record TV RS", "Record TV SP",
    "TV Aratu", "Rede CNT Salvador", "Record TV Belém", "Record TV Rio", "Record TV Goiás",
    "Record TV Interior SP", "Record TV Belem", "Record TV Goias", "RecordTV Interior SP"
}

# Constantes de ID de cor mapeadas no motor principal
cor_selecionado = 1
cor_normal = 2
cor_titulo = 3

LETRAS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def agrupar_por_letra(canais):
    canais_agrupados = {}
    for letra in LETRAS:
        canais_agrupados[letra] = []
    
    canais_agrupados["#"] = []
    
    for canal in canais:
        primeira_letra = canal['nome'][0].upper()
        if primeira_letra.isalpha():
            if primeira_letra in canais_agrupados:
                canais_agrupados[primeira_letra].append(canal)
            else:
                canais_agrupados["#"].append(canal)
        else:
            canais_agrupados["#"].append(canal)
    
    return canais_agrupados

def baixadar_e_processar_m3u():
    canais = []
    urls_vistas = set() 
    erros = []
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for arquivo_m3u in M3U_FILES:
        caminho_arquivo = os.path.join(base_dir, arquivo_m3u)
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
        except FileNotFoundError:
            erros.append(f"Arquivo não encontrado: {arquivo_m3u}")
            continue
        except IOError as e:
            erros.append(f"Erro ao ler arquivo {arquivo_m3u}: {e}")
            continue

        linhas = conteudo.split('\n')
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            if linha.startswith('#EXTINF'):
                nome = "Desconhecido"
                categoria = "Sem categoria"
                
                if ',' in linha:
                    nome = linha.split(',')[-1].strip()
                
                if 'group-title=' in linha:
                    inicio = linha.find('group-title="') + 13
                    fim = linha.find('"', inicio)
                    if inicio > 12 and fim > inicio:
                        categoria = linha[inicio:fim]
                
                i += 1
                while i < len(linhas) and not linhas[i].strip().startswith('http'):
                    i += 1
                
                if i < len(linhas):
                    url = linhas[i].strip()
                    if url.startswith('http'):
                        ignorado = False
                        for canal_ignorado in CANAIS_IGNORADOS:
                            if canal_ignorado.lower() in nome.lower():
                                ignorado = True
                                break
                        
                        if not ignorado and url not in urls_vistas:
                            canais.append({
                                "nome": f"{nome} [{arquivo_m3u[:6]}]",
                                "categoria": categoria,
                                "url": url
                            })
                            urls_vistas.add(url)
            i += 1
    
    if not canais:
        return None, "\n".join(erros) if erros else "As listas estavam vazias ou todos os canais foram ignorados."
        
    return canais, None

def verificar_mpv():
    try:
        subprocess.run(['/usr/bin/mpv', '--version'], capture_output=True, timeout=5)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def preparar_url_stream(url):
    if 'ottera.tv' in url:
        device_id = str(uuid.uuid4())
        if '?' in url:
            url += f"&device_id={device_id}&app_name=web&platform=web"
        else:
            url += f"?device_id={device_id}&app_name=web&platform=web"
    return url

def tocar_canal(stdscr, canal):
    curses.endwin()
    
    url_final = preparar_url_stream(canal['url']).strip()
    user_agent = random.choice(USER_AGENTS)
    
    console.print(f"\n[neon]📺 Sintonizando: [bold]{canal['nome']}[/bold]...[/neon]")
    console.print("[neon]▶ Pressione [bold]Q[/bold] no player para fechar suavemente.[/neon]")
    console.print("[neon]▶ Pressione [bold]Ctrl+C[/bold] no terminal para abortar conexão travada.[/neon]")
    sys.stdout.flush()
    
    os.system("killall mpv 2>/dev/null")
    
    comando = [
        '/usr/bin/mpv', 
        '--fs', 
        f'--user-agent={user_agent}',
        url_final
    ]
    
    try:
        subprocess.run(comando, check=False, stderr=None, stdout=None)
    except FileNotFoundError:
        console.print("[bold red]❌ Erro: mpv não encontrado em /usr/bin/mpv![/bold red]")
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⚠️ Conexão abortada pelo Operador (Ctrl+C).[/bold yellow]")
        os.system("killall mpv 2>/dev/null")
    
    console.print("\n[neon]↩️ Retornando ao catálogo...[/neon]")
    
    time.sleep(2)
    subprocess.run(['clear'])
    
    stdscr.clear()
    curses.curs_set(0)

def desenhar_interface(stdscr, canais, indice, offset, canais_agrupados, letra_atual):
    altura, largura = stdscr.getmaxyx()
    
    stdscr.clear()
    
    titulo = "📺 TELEMANIAX 📺"
    stdscr.addstr(0, (largura - len(titulo)) // 2, titulo, curses.color_pair(cor_titulo) | curses.A_BOLD)
    
    stdscr.addstr(1, 0, "=" * largura, curses.A_DIM)
    
    barra_letras = "[" + "][".join(LETRAS) + "]"
    stdscr.addstr(2, max(0, (largura - len(barra_letras)) // 2), barra_letras[:largura], curses.A_DIM)
    
    stdscr.addstr(3, 0, "=" * largura, curses.A_DIM)
    
    info = f"Letra: [{letra_atual}] | Total: {len(canais)} canais unificados"
    stdscr.addstr(4, 2, info[:largura-3], curses.A_DIM)
    stdscr.addstr(5, 0, "-" * largura, curses.A_DIM)
    
    pos_x_letra = 2 + LETRAS.index(letra_atual) * 3
    if pos_x_letra < largura - 3:
        stdscr.addstr(2, pos_x_letra, f"[{letra_atual}]", curses.color_pair(cor_selecionado) | curses.A_BOLD)
    
    stdscr.addstr(altura - 2, 0, "=" * largura, curses.A_DIM)
    
    rodape = "TELEMANIAX | [A-Z] Letra | [↑/↓] Navegar | [ENTER] Play | [ESC] Sair"
    x_pos = max(0, (largura - len(rodape)) // 2)
    rodape_seguro = rodape[:largura - x_pos - 1]
    
    try:
        stdscr.addstr(altura - 1, x_pos, rodape_seguro, curses.A_DIM)
    except curses.error:
        pass 
    
    limite = altura - 10
    start_y = 6
    
    canais_letra = canais_agrupados.get(letra_atual, [])
    
    for i, canal in enumerate(canais_letra[offset:offset + limite]):
        idx = offset + i
        linha = f"[{idx}] - {canal['nome']}"
        
        if start_y + i < altura - 2:
            try:
                if idx == indice:
                    stdscr.addstr(start_y + i, 2, linha[:largura - 3], curses.color_pair(cor_selecionado) | curses.A_BOLD)
                else:
                    stdscr.addstr(start_y + i, 2, linha[:largura - 3], curses.color_pair(cor_normal))
            except curses.error:
                pass
    
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    
    # Motor de Cores Centralizado - Herança Nativa (Relevo Baixo)
    curses.start_color()
    curses.use_default_colors() # Permite o uso do fundo real do terminal
    
    # O valor -1 mapeia diretamente para o background/foreground nativo do emulador
    curses.init_pair(cor_selecionado, curses.COLOR_GREEN, -1)
    curses.init_pair(cor_normal, curses.COLOR_GREEN, -1)
    curses.init_pair(cor_titulo, curses.COLOR_GREEN, -1)
    
    stdscr.bkgd(' ', curses.color_pair(cor_normal))
    
    if not verificar_mpv():
        curses.endwin()
        console.print("\n[bold red]❌ Erro: mpv não encontrado![/bold red]")
        console.print("[neon]Instale com: sudo apt install mpv[/neon]\n")
        sys.exit(1)
    
    stdscr.addstr(0, 0, "Carregando Hub Central em Relevo Baixo...", curses.color_pair(cor_normal))
    stdscr.refresh()
    
    canais, erro = baixadar_e_processar_m3u()
    
    if not canais:
        curses.endwin()
        console.print("\n[bold red]❌ Falha ao carregar as listas.[/bold red]")
        if erro:
            console.print(f"[neon]Detalhes do erro:\n{erro}[/neon]\n")
        sys.exit(1)
    
    canais_agrupados = agrupar_por_letra(canais)
    
    letra_atual = "A"
    indice = 0
    offset = 0
    
    while True:
        altura, _ = stdscr.getmaxyx()
        limite = altura - 10
        
        canais_letra = canais_agrupados.get(letra_atual, [])
        total_letra = len(canais_letra)
        
        if total_letra == 0:
            if LETRAS.index(letra_atual) < len(LETRAS) - 1:
                idx_prox = LETRAS.index(letra_atual) + 1
                while idx_prox < len(LETRAS):
                    if len(canais_agrupados[LETRAS[idx_prox]]) > 0:
                        letra_atual = LETRAS[idx_prox]
                        break
                    idx_prox += 1
            canais_letra = canais_agrupados.get(letra_atual, [])
            total_letra = len(canais_letra)
        
        if indice < offset:
            offset = indice
        elif indice >= offset + limite:
            offset = indice - limite + 1
        
        desenhar_interface(stdscr, canais, indice, offset, canais_agrupados, letra_atual)
        
        tecla = stdscr.getch()
        
        if tecla == 27:  # ESC
            break
        elif tecla == ord('\n') and total_letra > 0:
            tocar_canal(stdscr, canais_letra[indice])
        elif tecla == curses.KEY_UP:
            if indice > 0:
                indice -= 1
                if indice < offset:
                    offset = max(0, indice - limite + 1)
        elif tecla == curses.KEY_DOWN:
            if indice < total_letra - 1:
                indice += 1
        elif tecla == curses.KEY_HOME:
            indice = 0
            offset = 0
        elif tecla == curses.KEY_END:
            indice = max(0, total_letra - 1)
        elif tecla == curses.KEY_PPAGE:
            indice = max(0, indice - 10)
            offset = max(0, offset - 10)
        elif tecla == curses.KEY_NPAGE:
            indice = min(total_letra - 1, indice + 10)
            offset = min(max(0, total_letra - limite), offset + 10)
        else:
            letra_press = chr(tecla).upper()
            if letra_press in LETRAS and len(canais_agrupados.get(letra_press, [])) > 0:
                letra_atual = letra_press
                offset = 0
                indice = 0

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        console.print("\n[neon]📡 Sessão encerrada. Guarda alta, operador.[/neon]\n")
        os.system("killall mpv 2>/dev/null") 
        sys.exit(0)