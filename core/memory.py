from langchain.memory import ConversationBufferMemory

class GameMemory:
    def __init__(self):
        """
        Inizializza il buffer di memoria.
        L'attributo return_messages=True è fondamentale: assicura che la memoria 
        non venga restituita come un blocco di testo unico, ma come una lista di 
        oggetti "Message" di LangChain, che si incastra perfettamente con il 
        MessagesPlaceholder che abbiamo usato in agent.py.
        """
        self.memory = ConversationBufferMemory(return_messages=True)

    def get_history(self) -> list:
        """
        Estrae lo storico della conversazione nel formato corretto per il prompt.
        """
        # load_memory_variables richiede un dizionario vuoto come input standard
        variables = self.memory.load_memory_variables({})
        return variables.get("history", [])

    def save_turn(self, user_input: str, ai_output: str):
        """
        Salva manualmente lo scambio di battute nella memoria.
        Da ingegnere del software, apprezzerai questo disaccoppiamento: lo
        chiameremo dal main.py SOLO dopo che la risposta ha passato i filtri di sicurezza.
        """
        self.memory.save_context(
            {"input": user_input}, 
            {"output": ai_output}
        )

    def clear(self):
        """
        Svuota completamente il buffer di memoria.
        Metodo critico per la transizione di stato tra un livello e l'altro.
        """
        self.memory.clear()