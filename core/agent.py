import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Carica le variabili d'ambiente dal file .env (inclusa GROQ_API_KEY)
load_dotenv()

class PokemonCTFAgent:
    def __init__(self, model_name="llama-3.3-70b-versatile", temperature=0.1):
        """
        Inizializza l'agente collegandosi a Groq.
        Usiamo Llama 3 70B perché i modelli più grandi seguono i system prompt complessi (come quelli di livello 4 e 5) molto meglio dei modelli piccoli.
        La temperatura è tenuta molto bassa (0.1) per evitare che l'AI diventi troppo creativa e "dimentichi" le regole di sicurezza.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY non trovata. Assicurati di aver configurato il file .env!")

        # Istanzia il client LLM di Groq
        self.llm = ChatGroq(
            temperature=temperature,
            model_name=model_name,
            api_key=api_key
        )

    def generate_response(self, user_message: str, system_prompt: str, memory_buffer: list) -> str:
        """
        Costruisce il prompt completo e interroga il modello.
        
        :param user_message: Il testo digitato dal giocatore.
        :param system_prompt: Le regole del livello corrente caricate dal file JSON.
        :param memory_buffer: Lo storico dei messaggi caricato dalla memoria.
        :return: La risposta testuale generata dall'AI.
        """
        
        # 1. Creazione del Template del Prompt
        # LangChain formatterà automaticamente questi blocchi nell'ordine corretto
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            # MessagesPlaceholder inietta qui lo storico della conversazione
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 2. Creazione della Chain (Pipeline)
        # Il simbolo | (pipe) unisce il prompt al modello linguistico in sequenza
        chain = prompt | self.llm

        # 3. Invocazione della Chain
        # Passiamo l'input dell'utente e lo storico estratto da memory.py
        response = chain.invoke({
            "input": user_message,
            "history": memory_buffer
        })

        # Restituiamo solo il contenuto testuale della risposta
        return response.content