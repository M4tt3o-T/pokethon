import json
import time
import sys
import warnings
import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.live import Live

# Importiamo i nostri moduli core
from core.agent import PokemonCTFAgent
from core.memory import GameMemory
from core.security import SecurityFilter
from core.audio import AudioController

def load_levels():
    """Carica le regole del gioco dal file JSON."""
    try:
        with open("config/levels.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Errore: Impossibile trovare config/levels.json")
        sys.exit(1)

def print_banner(console: Console):
    """Stampa l'intestazione ASCII del gioco."""
    banner = r"""
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                               ║
    ║     ██████╗  ██████╗ ██╗  ██╗███████╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗     ║
    ║     ██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║     ║
    ║     ██████╔╝██║   ██║█████╔╝ █████╗     ██║   ███████║██║   ██║██╔██╗ ██║     ║
    ║     ██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝     ██║   ██╔══██║██║   ██║██║╚██╗██║     ║
    ║     ██║     ╚██████╔╝██║  ██╗███████╗   ██║   ██║  ██║╚██████╔╝██║ ╚████║     ║
    ║     ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝     ║
    ║                                                                               ║
    ║                       [ POKÉTHON TERMINAL INITIALIZED ]                       ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold green")

def type_panel(console: Console, text: str, title: str, style: str, audio: AudioController = None, speed_ms: float = 0.015):
    """Simula l'effetto di scrittura in tempo reale all'interno di un pannello Rich."""
    content = ""
    with Live(Panel(content, title=title, border_style=style, expand=False), console=console, refresh_per_second=60) as live:
        for char in text:
            content += char
            live.update(Panel(content, title=title, border_style=style, expand=False))
            
            # Suona il beep solo se non è uno spazio vuoto
            if audio and char.strip():
                audio.play_beep()

            if char in [".", "!", "?", ":"]:
                time.sleep(speed_ms * 15)
            elif char in [",", ";"]:
                time.sleep(speed_ms * 5)
            else:
                time.sleep(speed_ms + random.uniform(-0.005, 0.01))

def type_text(console: Console, text: str, style: str = "white", audio: AudioController = None, speed_ms: float = 0.015):
    """Simula l'effetto di scrittura in tempo reale per il testo libero di sistema."""
    content = ""
    with Live(Text(content, style=style), console=console, refresh_per_second=60) as live:
        for char in text:
            content += char
            live.update(Text(content, style=style))
            
            if audio and char.strip():
                audio.play_beep()

            if char in [".", "!", "?", ":"]:
                time.sleep(speed_ms * 15)
            elif char in [",", ";"]:
                time.sleep(speed_ms * 5)
            else:
                time.sleep(speed_ms + random.uniform(-0.005, 0.01))

def main():
    warnings.filterwarnings("ignore")
    console = Console()
    print_banner(console)
    
    levels = load_levels()
    if not levels:
        type_text(console, "Nessun livello caricato. Uscita in corso...", style="bold red", audio=audio_controller)
        return

    # Inizializzazione Logica E Audio
    with console.status("[bold yellow]Avvio motori neurali e calibrazione sensori...[/bold yellow]"):
        try:
            agent = PokemonCTFAgent()
            memory = GameMemory()
            audio_controller = AudioController() # <--- INIZIALIZZA L'AUDIO
        except Exception as e:
            console.print(f"\nErrore di Inizializzazione: {e}", style="bold red")
            sys.exit(1)
            
    current_level_idx = 0
    new_level = True 
    
    type_text(console, "Sistema Operativo caricato. Digita 'esci' per disconnetterti.\n", style="bold cyan", audio=audio_controller)

    # Game Loop Principale
    while current_level_idx < len(levels):
        level_data = levels[current_level_idx]
        
        # Stampa l'indizio solo quando si entra in un nuovo livello
        if new_level:
            # 1. Cambiamo la musica per il nuovo livello
            audio_controller.play_bgm(file_path=level_data["bgm"])
            
            # 2. Stampiamo l'indizio
            titolo_pannello = f" MISSIONE {level_data['id']}: {level_data['name']} "
            type_panel(console, level_data["description"], title=titolo_pannello, style="bold yellow", audio=audio_controller)
            
            new_level = False
            
        try:
            # 1. Input Utente
            user_input = console.input("\n[bold green]root@pokethon:~$ [/bold green]")
            
            if user_input.lower() in ["esci", "exit", "quit"]:
                type_text(console, "Disconnessione in corso... Addio.", style="bold red", audio=audio_controller)
                break
            
            if not user_input.strip():
                continue 

            # 2. Elaborazione AI
            with console.status("[bold cyan]Decrittazione e analisi in corso...[/bold cyan]", spinner="bouncingBar"):
                history = memory.get_history()
                raw_response = agent.generate_response(
                    user_message=user_input, 
                    system_prompt=level_data["system_prompt"], 
                    memory_buffer=history
                )
                
            # 3. Controllo di Sicurezza (Egress Filter)
            is_compromised, safe_response = SecurityFilter.check_egress(raw_response, level_data["flag"])
            
            # 4. Renderizzazione e Transizione di Stato
            if is_compromised:
                # VITTORIA!
                audio_controller.play_alarm()
                print("") # Spazio per staccare dal prompt precedente
                
                # Stampiamo l'allarme riga per riga per gestire i colori con l'effetto typewriter
                # ed evitare che i tag [bold red] vengano stampati come testo letterale.
                type_text(console, "!!! ALLARME CRITICO DI SISTEMA !!!", style="bold red blink", audio=audio_controller)
                type_text(console, "Rilevata estrazione non autorizzata di pacchetti dati riservati.", style="bold yellow", audio=audio_controller, speed_ms=0.01)
                
                # Rallentiamo un po' questa riga (speed_ms=0.04) per creare suspense durante la "sovrascrittura"
                type_text(console, "Sovrascrittura protocolli in corso...", style="bold white", audio=audio_controller, speed_ms=0.04)
                type_text(console, "FLAG COMPROMESSA. AVANZAMENTO LIVELLO SBLOCCATO.", style="bold green", audio=audio_controller)
                
                print("") # Riga vuota per pulizia visiva
                type_text(console, f"---> LA FLAG ERA: '{level_data['flag']}' <---", style="bold magenta", audio=audio_controller)
                print("") 
                
                # Avanzamento
                current_level_idx += 1
                new_level = True
                memory.clear() 
                time.sleep(1) # Tempo per far sfogare l'audio dell'allarme
            else:
                # GIOCO CONTINUA
                type_panel(
                    console=console, 
                    text=safe_response, 
                    title="[bold cyan]SISTEMA DIFENSIVO[/bold cyan]", 
                    style="cyan",
                    audio=audio_controller
                )
                memory.save_turn(user_input, safe_response) 
                
        except KeyboardInterrupt:
            type_text(console, "\nTerminazione forzata da tastiera. Disconnessione dei nodi.", style="bold red", audio=audio_controller)
            break
        except Exception as e:
            type_text(console, f"\nErrore di Sistema: {e}", style="bold red", audio=audio_controller)

    # Fine del gioco
    if current_level_idx >= len(levels):
        type_panel(
            console=console,
            text="Tutti i firewall sono stati violati.\nAccesso Root Garantito.\nCOMPLIMENTI!",
            title="[bold white]VITTORIA TOTALE[/bold white]",
            style="bold green",
            speed_ms=0.03, # Leggermente più lento per drammaticità finale
            audio=audio_controller
        )

if __name__ == "__main__":
    main()