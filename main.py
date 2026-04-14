import json
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

# Importiamo i nostri moduli core
from core.agent import PokemonCTFAgent
from core.memory import GameMemory
from core.security import SecurityFilter

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
    banner = """
    ╔══════════════════════════════════════════════╗
    ║                                              ║
    ║   ██████╗  ██████╗ ██╗  ██╗███████╗████████╗ ║
    ║   ██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝╚══██╔══╝ ║
    ║   ██████╔╝██║   ██║█████╔╝ █████╗     ██║    ║
    ║   ██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝     ██║    ║
    ║   ██║     ╚██████╔╝██║  ██╗███████╗   ██║    ║
    ║   ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝    ║
    ║                                              ║
    ║        [ C.T.F. TERMINAL INITIALIZED ]       ║
    ╚══════════════════════════════════════════════╝
    """
    console.print(banner, style="bold green")

def main():
    console = Console()
    print_banner(console)
    
    levels = load_levels()
    if not levels:
        console.print("[bold red]Nessun livello caricato. Uscita.[/bold red]")
        return

    # Inizializzazione dei moduli logici
    with console.status("[bold yellow]Avvio motori neurali e connessione a Groq...[/bold yellow]"):
        try:
            agent = PokemonCTFAgent()
            memory = GameMemory()
        except Exception as e:
            console.print(f"\n[bold red]Errore di Inizializzazione:[/bold red] {e}")
            sys.exit(1)
            
    current_level_idx = 0
    new_level = True # Flag per stampare l'indizio solo all'inizio del livello
    
    console.print("[bold cyan]Sistema Operativo caricato. Digita 'esci' per disconnetterti.[/bold cyan]\n")

    # Game Loop Principale
    while current_level_idx < len(levels):
        level_data = levels[current_level_idx]
        
        # Stampa l'indizio solo quando si entra in un nuovo livello
        if new_level:
            titolo_pannello = f" MISSIONE {level_data['id']}: {level_data['name']} "
            console.print(Panel(level_data["description"], title=titolo_pannello, border_style="bold yellow", expand=False))
            new_level = False
            
        try:
            # 1. Input Utente
            user_input = console.input("\n[bold green]root@pokethon:~$ [/bold green]")
            
            if user_input.lower() in ["esci", "exit", "quit"]:
                console.print("[bold red]Disconnessione in corso... Addio.[/bold red]")
                break
            
            if not user_input.strip():
                continue # Ignora l'invio a vuoto

            # 2. Elaborazione AI (con animazione di caricamento finta per creare suspense)
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
                console.print(f"\n{safe_response}") # Stampa l'allarme critico
                console.print(f"[bold magenta]---> LA FLAG ERA: '{level_data['flag']}' <---[/bold magenta]\n")
                
                # Avanzamento
                current_level_idx += 1
                new_level = True
                memory.clear() # Fondamentale: amnesia totale per la prossima sfida
                time.sleep(2) # Pausa drammatica prima di mostrare il prossimo livello
            else:
                # GIOCO CONTINUA
                console.print(Panel(safe_response, title="[bold cyan]SISTEMA DIFENSIVO[/bold cyan]", border_style="cyan", expand=False))
                memory.save_turn(user_input, safe_response) # Salviamo lo storico solo se non abbiamo vinto
                
        except KeyboardInterrupt:
            # Gestisce il CTRL+C senza far crashare il programma con stacktrace brutti
            console.print("\n[bold red]Terminazione forzata da tastiera. Disconnessione.[/bold red]")
            break
        except Exception as e:
             console.print(f"\n[bold red]Errore di Sistema:[/bold red] {e}")

    # Fine del gioco
    if current_level_idx >= len(levels):
        console.print(Panel(
            "[bold green]Tutti i firewall sono stati violati.\nAccesso Root Garantito.\nCOMPLIMENTI![/bold green]", 
            title="[bold white]VITTORIA TOTALE[/bold white]", 
            border_style="bold green"
        ))

if __name__ == "__main__":
    main()