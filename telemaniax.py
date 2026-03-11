#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import requests
import subprocess
import os
import sys
import uuid

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "neon": "bold green",
})

console = Console(theme=custom_theme)

APP_NAME = "TELEMANIAX"
VERSION = "1.0.0"
M3U_URL = "https://iptv-org.github.io/iptv/countries/br.m3u"

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

cor_selecionado = 1
cor_normal = 2
cor_titulo = 3

def baixar_e_processar_m3u():
    try:
        resposta = requests.get(M3U_URL, timeout=30)
        resposta.raise_for_status()
    except requests.RequestException as e:
        return None, f"Erro ao baixar lista de canais: {e}"

    canais = []
    linhas = resposta.text.split('\n')
    
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
                    if not ignorado:
                        canais.append({
                            "nome": nome,
                            "categoria": categoria,
                            "url": url
                        })
        i += 1
    
    return canais, None

def verificar_mpv():
    try:
        subprocess.run(['mpv', '--version'], capture_output=True, timeout=5)
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
    url_final = preparar_url_stream(canal['url'])
    
    console.print(f"\n[neon]📺 Sintonizando: [bold]{canal['nome']}[/bold]...[/neon]")
    console.print("[neon]▶ Pressione [bold]Q[/bold] na janela do mpv para fechar.[/neon]")
    sys.stdout.flush()
    
    try:
        subprocess.run([
            'mpv', 
            '--fs', 
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            '--http-header-fields=Referer: https://www.google.com/, Origin: https://www.google.com/',
            url_final
        ], check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        console.print("[bold red]❌ Erro: mpv não encontrado![/bold red]")
        console.print("[neon]Instale com: sudo apt install mpv[/neon]")
    
    console.print("\n[neon]↩️ A voltar ao menu...[/neon]")
    subprocess.run(['clear'])
    stdscr.clear()
    curses.curs_set(0)

def desenhar_interface(stdscr, canais, indice, offset):
    altura, largura = stdscr.getmaxyx()
    
    curses.start_color()
    curses.init_pair(cor_selecionado, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(cor_normal, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(cor_titulo, curses.COLOR_GREEN, curses.COLOR_BLACK)
    
    stdscr.clear()
    stdscr.bkgd(' ', curses.color_pair(cor_normal))
    
    titulo = "📺 TELEMANIAX 📺"
    stdscr.addstr(0, (largura - len(titulo)) // 2, titulo, curses.color_pair(cor_titulo) | curses.A_BOLD)
    stdscr.addstr(1, 0, "=" * largura, curses.A_DIM)
    
    stdscr.addstr(altura - 2, 0, "=" * largura, curses.A_DIM)
    rodape = "TELEMANIAX | [↑/↓] Navegar | [ENTER] Assistir | [Q] Sair"
    stdscr.addstr(altura - 1, (largura - len(rodape)) // 2, rodape, curses.A_DIM)
    
    info = f"Total de canais: {len(canais)} | Canal: {indice + 1}"
    stdscr.addstr(2, 2, info, curses.A_DIM)
    stdscr.addstr(3, 0, "-" * largura, curses.A_DIM)
    
    limite = altura - 5
    start_y = 4
    
    for i, canal in enumerate(canais[offset:offset + limite]):
        idx = offset + i
        linha = f"[{idx}] - {canal['nome']}"
        
        if idx == indice:
            stdscr.addstr(start_y + i, 2, linha[:largura - 3], curses.color_pair(cor_selecionado) | curses.A_BOLD)
        else:
            stdscr.addstr(start_y + i, 2, linha[:largura - 3], curses.color_pair(cor_normal))
    
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.use_default_colors()
    stdscr.bkgd(' ', curses.COLOR_BLACK)
    
    if not verificar_mpv():
        curses.endwin()
        console.print("\n[bold red]❌ Erro: mpv não encontrado![/bold red]")
        console.print("[neon]Instale com: sudo apt install mpv[/neon]\n")
        sys.exit(1)
    
    stdscr.addstr(0, 0, "Baixando canais...", curses.COLOR_GREEN)
    stdscr.refresh()
    
    canais, erro = baixar_e_processar_m3u()
    
    if erro:
        curses.endwin()
        console.print(f"\n[bold red]❌ Erro: {erro}[/bold red]\n")
        sys.exit(1)
    
    if not canais:
        curses.endwin()
        console.print("\n[neon]⚠️ Nenhum canal encontrado.[/neon]\n")
        sys.exit(1)
    
    indice = 0
    offset = 0
    
    while True:
        altura, _ = stdscr.getmaxyx()
        limite = altura - 5
        
        if indice < offset:
            offset = indice
        elif indice >= offset + limite:
            offset = indice - limite + 1
        
        desenhar_interface(stdscr, canais, indice, offset)
        
        tecla = stdscr.getch()
        
        if tecla == ord('q') or tecla == ord('Q'):
            break
        elif tecla == ord('\n'):
            tocar_canal(stdscr, canais[indice])
        elif tecla == curses.KEY_UP:
            if indice > 0:
                indice -= 1
        elif tecla == curses.KEY_DOWN:
            if indice < len(canais) - 1:
                indice += 1
        elif tecla == curses.KEY_HOME:
            indice = 0
        elif tecla == curses.KEY_END:
            indice = len(canais) - 1
        elif tecla == curses.KEY_PPAGE:
            indice = max(0, indice - 10)
        elif tecla == curses.KEY_NPAGE:
            indice = min(len(canais) - 1, indice + 10)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        console.print("\n[neon]📡 Sessão encerrada. Até logo![/neon]\n")
        sys.exit(0)
