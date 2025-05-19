import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
import pandas as pd
import requests
from atlassian import Jira
import time

# Carica le variabili d'ambiente
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  
JIRA_URL = os.getenv("JIRA_URL")  
JIRA_USERNAME = os.getenv("JIRA_USERNAME")  
JIRA_TOKEN = os.getenv("JIRA_TOKEN")  

wait_time = 60
max_retries = 3 

# Configurazione iniziale
st.set_page_config(
    page_title="(TEST)INA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

max_retries=10

# Database di conoscenza (come nell'originale)
KNOWLEDGE_BASE = {
            "PAE": {
                "nome": "PAE",
                "descrizione": "Portale per la gestione dei diritti d’autore, iscrizioni e pagamenti.",
                "tipologia": "Frontend",
                "accessibilita": ["Front Office", "Back Office"],
                "utenti_accessibili": ["Autori", "Editori"],
                "scopo_principale": "Consentire ad autori ed editori di gestire i propri diritti, dichiarare opere e monitorare compensi.",
                "casi_d'uso": [
                    "Registrazione di nuove opere",
                    "Dichiarazione dei redditi da diritto d’autore",
                    "Consultazione pagamenti",
                    "Invio richieste di assistenza"
                ]
            },
            "POP": {
                "nome": "POP",
                "descrizione": "Portale per l’acquisizione e la gestione delle licenze per eventi pubblici con musica dal vivo o registrata.",
                "tipologia": "Frontend",
                "accessibilita": ["Front Office"],
                "utenti_accessibili": ["Organizzatori di eventi", "Aziende"],
                "scopo_principale": "Digitalizzare il processo di richiesta di licenze e permessi per eventi.",
                "casi_d'uso": [
                    "Richiesta di licenze per eventi",
                    "Calcolo e pagamento dei diritti",
                    "Gestione delle pratiche autorizzative"
                ]
            },
            "Music&Go": {
                "nome" : "Music&GO - Concertini",
                "descrizione": "Servizio online per il rilascio immediato di licenze per concertini dal vivo in bar o ristoranti",
                "tipologia": "Frontend",
                "accessibilita": ["Front Office"],
                "utenti_accessibili": ["Artisti", "Locali", "Delegati"],
                "scopo_principale": "Semplificare il processo di autorizzazione e pagamento per spettacoli musicali in pubblici esercizi",
                "casi_d'uso": [
                    "Richiesta di licenza per evento musicale",
                    "Pagamento dei diritti online",
                    "Consultazione storico licenze acquisite",
                    "Emissione ricevute e fatture"
                ]
            },
            "DJ": {
                "nome": "DJ Online",
                "descrizione": "Piattaforma per la licenza e la gestione della musica per DJ e locali.",
                "tipologia": "Frontend",
                "accessibilita": ["Front Office"],
                "utenti_accessibili": ["DJ", "Gestori Locali"],
                "scopo_principale": "Permettere ai DJ di ottenere licenze per l’utilizzo di musica in pubblico.",
                "casi_d'uso": [
                    "Richiesta licenza annuale DJ",
                    "Dichiarazione utilizzo brani",
                    "Consultazione normativa e tariffe",
                    "Pagamento online dei diritti"
                ]
            },
            "Mioborderò Organizzatore": {
                "descrizione": "Servizio per la dichiarazione delle esecuzioni musicali da parte dell’organizzatore di eventi.",
                "tipologia": "Frontend",
                "accessibilita": ["Front Office"],
                "utenti_accessibili": ["Organizzatori Eventi"],
                "scopo_principale": "Digitalizzare la raccolta e l’invio dei borderò con il dettaglio delle esecuzioni musicali, assegnando prima l'esecuzione al direttore di esecuzione.",
                "casi_d'uso": [
                    "Compilazione e invio borderò",
                    "Associazione borderò a licenza evento",
                    "Consultazione storico eventi",
                    "Verifica obblighi di pagamento"
                ]
            },
            "Mioborderò Direttore Esecuzione": {
                "descrizione": "Servizio per la dichiarazione delle esecuzioni musicali da parte del direttore dell’esecuzione.",
                "tipologia": "Frontend",
                "accessibilita": ["Front Office"],
                "utenti_accessibili": ["Direttori d’Esecuzione", "Musicisti"],
                "scopo_principale": "Consentire ai musicisti di dichiarare l’elenco dei brani eseguiti durante un evento.",
                "casi_d'uso": [
                    "Dichiarazione delle opere eseguite",
                    "Firma digitale del borderò",
                    "Consultazione storico esibizioni",
                    "Comunicazione con SIAE"
                ]
            },
            "LOL": {
                "descrizione": "Portale per la richiesta di licenze per l’utilizzo di opere figurative tutelate da SIAE.",
                "tipologia": "Frontend",
                "accessibilita": ["Front Office", "Back Office"],
                "utenti_accessibili": ["Artisti", "Galleristi", "Editori", "Aziende di Merchandising"],
                "scopo_principale": "Fornire un sistema per la gestione dei diritti sulle opere visive utilizzate su prodotti stampati e commercializzati.",
                "casi_d'uso": [
                    "Richiesta licenza per l’uso di immagini su merchandising",
                    "Autorizzazione per la pubblicazione di opere su libri e riviste",
                    "Gestione diritti per mostre ed esposizioni",
                    "Calcolo e pagamento compensi SIAE"
                ]
            },
            "GOAL": {
                "descrizione": "Piattaforma per la richiesta di licenze per servizi musicali online.",
                "tipologia": "Frontend",
                "accessibilita": ["Front Office", "Back Office"],
                "utenti_accessibili": ["Privati", "Persone fisiche", "Organizzazioni", "Aziende"],
                "scopo_principale": "Permettere agli operatori digitali di ottenere le licenze necessarie per la diffusione di musica online.",
                "casi_d'uso": [
                    "Richiesta di licenza per podcast con musica protetta",
                    "Ottenimento di autorizzazioni per Web TV con contenuti musicali",
                    "Licenze per eventi live streaming con musica",
                    "Regolamentazione dell’uso musicale su piattaforme VOD"
                ]
            },
            "TTPP": {
                "descrizione": "Servizio per la richiesta e gestione delle licenze per feste  private con musica.",
                "tipologia": "Frontend",
                "accessibilita": ["Front Office"],
                "utenti_accessibili": ["Privati"],
                "scopo_principale": "Semplificare il processo di ottenimento dei permessi per feste private.",
                "casi_d'uso": [
                    "Richiesta licenza per festa privata",
                    "Pagamento online dei diritti",
                    "Download documentazione licenza",
                    "Verifica normativa vigente"
                ]
            },
            "BIGLIETTERIA": {
                "descrizione": "Sistema di gestione della biglietteria integrato con SPORT per la sincronizzazione automatica di comuni, SEPRAG, stradario e codici BA.",
                "tipologia": "Backend/Frontend",
                "accessibilita": ["Front Office", "Back Office", "Automatico"],
                "utenti_accessibili": ["Operatori Biglietteria", "Amministratori Sistema", "Sistema"],
                "scopo_principale": "La certificazione degli incassi nel settore degli spettacoli e degli intrattenimenti avviene tramite apparecchiature “biglietterie automatizzate”",
                "casi_d'uso": [
                    "Il sistema di bigliettera crea un reporto degli incassi giornalieri, per singolo evento, per tutti gli eventi regolari in Italia",
                    "Il sistema di biglietteria crea un report mensile dei biglietti erogati, per singolo evento, per tutti gli eventi regolari in Italia",
                    "Il sistema invia i rendiconti dei dati a SPORT tramite un batch"
                ]
            },
            "SPORT": {
                "descrizione": "Sistema di gestione delle operazioni di Sportello della SIAE.",
                "tipologia": "Backend/Frontend",
                "accessibilita": ["Back Office"],
                "utenti_accessibili": ["Operatori Mandatarie", "Amministratori Sistema", "Sistema", "Mandatarie", "Superuser"],
                "scopo_principale": "La gestione automatizzata di tutte le procedure di incasso e accertamenti, che permette di svolgere le operazioni di sportello come pagare e generare licenze, caricare i locali e le loro anagrafiche, caricare gli accertamenti autorali e relative audioni, schede di musica d'ambiente, licenze concertini, licenze pop”",
                "casi_d'uso": [
                    "Il sistema gestisce il ciclo di pagamento e rilascio licenza per mda",
                    "Il sistema gestisce il ciclo di pagamento e rilascio licenza per concertini",
                    "Il sistema gestisce il ciclo di pagamento per le relazioni derivanti dagli accertamenti autorali",
                    "Il sistema gestisce il ciclo di operazioni di sportello della SIAE",
                ]
            },
             "ULISSE": {
                "nome": "ULISSE",
                "descrizione": "Sistema di catalogo delle opere, musica, cinema e dor",
                "tipologia": "Backend/Frontend",
                "accessibilita": ["Back Office"],
                "utenti_accessibili": ["Operatori Mandatarie", "Amministratori Sistema", "Sistema", "Mandatarie", "Superuser"],
                "scopo_principale": "L'elenco delle opere musica, cinema, dor, depositate nell'archivio della SIAE",
                "casi_d'uso": [
                    "Il sistema gestisce l'inserimento e aggiornamento del repertorio opere della SIAE",
                ]
            },
}

def is_proxy_required(url="http://www.google.com", timeout=2):
    try:
        requests.get(url, timeout=timeout)
        return False  # Connection successful, no proxy needed
    except requests.exceptions.RequestException as e:
        print(f"Connection test failed: {e}")
        return True   # Connection failed, proxy might be needed

def get_jira_instance():
    try:
        session = requests.Session()
        if is_proxy_required():
            session.proxies = {
                'http': 'http://mazzacuv:GigiBuffon92!@10.255.1.243:8080',
                'https': 'http://mazzacuv:GigiBuffon92!@10.255.1.243:8080'
            }
        
        jira = Jira(
            url=JIRA_URL,
            username=JIRA_USERNAME,
            password=JIRA_TOKEN,
            session=session
        )
        return jira
    except Exception as e:
        st.error(f"Errore di connessione a Jira: {e}")
        return None

# Inizializza il client Google AI
def get_genai_client():
    return genai.Client(api_key=GEMINI_API_KEY)

def get_jira_projects(jira):
    """Recupera tutti i progetti da Jira."""
    if jira:
        try:
            projects = jira.projects()
            # Verifica il tipo di elemento in 'projects' per debug
            if projects and isinstance(projects[0], dict):
                return {project['key']: project['name'] for project in projects}  # Accesso tramite chiave
            else:
                return {project.key: project.name for project in projects} # Accesso tramite attributo (come prima)
        except Exception as e:
            st.error(f"Errore nel recupero dei progetti Jira: {e}")
            return {}
    else:
        return {}
        
def get_project_issues(jira, project_key, issue_types):
    """Recupera le issue di un progetto Jira."""

    if jira and project_key:
        jql_query = f"project={project_key} AND issuetype in ({','.join(issue_types)})"
        try:
            issues = jira.jql(jql_query)  # Usa jira.jql invece di jira.search_issues
            return issues['issues']  # Restituisce la lista di issue
        except Exception as e:
            st.error(f"Errore nel recupero delle issue: {e}")
            return []
    else:
        return []

def display_issue_details(issue):
    """Visualizza i dettagli di un'issue."""
    with st.expander(f"Dettagli: {issue['key']} - {issue['fields']['summary']}"):
        st.write(f"**Stato:** {issue['fields']['status']['name']}")
        st.write(f"**Creato:** {issue['fields']['created']}")
        st.write(f"**Assegnatario:** {issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Nessuno'}")
        st.write("**Descrizione:**")
        st.markdown(issue['fields']['description'] if issue['fields']['description'] else "Nessuna descrizione fornita.")

def run_valutatore_requisiti(requisito, client, model="gemini-2.0-flash-001"):
    prompt = f"""
    Sei un esperto nella valutazione e miglioramento dei requisiti software. Il tuo compito è valutare se il requisito fornito contiene tutte le informazioni necessarie per evitare ambiguità e incomprensioni nello sviluppo.
    
    Valuta il requisito in base ai seguenti criteri minimi (basati sugli standard delle user story):
    1. **Chi** - Chi è l'utente/attore principale (es. "Come [ruolo/utente]")
    2. **Cosa** - Cosa vuole ottenere (es. "voglio [funzionalità/obiettivo]")
    3. **Perché** - Perché lo vuole (es. "per [beneficio/scopo]")
    4. **Criteri di accettazione** - Condizioni che definiscono quando il requisito è soddisfatto
    5. **Contesto** - Informazioni sufficienti sul contesto d'uso
    6. **Dettagli tecnici** - Eventuali vincoli tecnici o specifiche
    
    Se il requisito è completo, confermalo e suggerisci eventuali piccoli miglioramenti.
    Se il requisito è incompleto, proporre una versione migliorata che includa tutti gli elementi mancanti, 
    usando segnaposto generici come [soggetto], [formato], [ruolo], [funzionalità], [beneficio], [condizione], 
    [vincolo] dove le informazioni specifiche mancano.
    
    Fornisci la tua valutazione in questo formato:
    
    ### Valutazione Completezza:
    [Valutazione complessiva: Requisito completo / Requisito parzialmente completo / Requsito incompleto]
    
    ### Elementi Presenti:
    - [Lista degli elementi presenti nel requisito]
    
    ### Elementi Mancanti:
    - [Lista degli elementi mancanti che dovrebbero essere aggiunti]
    
    ### Requisito Migliorato:
    [Versione migliorata del requisito con segnaposto generici per gli elementi mancanti]
    
    ### Note:
    [Eventuali note aggiuntive o spiegazioni]
    
    Ecco il requisito da valutare:
    {requisito}
    
    **Rispondi solo in italiano**
    """
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    
    return response.text

def run_analista_requisiti(requisito, client, model="gemini-2.0-flash-001"):
    context = ""
    for system_id, system_info in KNOWLEDGE_BASE.items():
        if system_id.lower() in requisito.lower():
            context = f"Informazioni dal knowledge base per il sistema {system_id}:\n"
            context += "\n".join([f"{key}: {value}" for key, value in system_info.items()])
    system_instruction = "Sei un assistente specializzato nell'analisi dei requisiti software. Rispondi in formato testo strutturato."
    prompt = f"""
    {system_instruction}
            
        1. Il contesto generale del requisito (di cosa si tratta, qual è l'obiettivo)
        2. I principali attori/utenti coinvolti
        3. Gli scenari d'uso:
           - Scenari principali (flusso normale)
           - Scenari alternativi (flussi alternativi plausibili)
           - Scenari negativi (situazioni in cui qualcosa non funziona)
           - Corner cases (situazioni limite)
        4. Le variabili dinamiche presenti nel requisito
        5. Flusso di lavoro strutturato
        
        Ecco il requisito da analizzare:    
    {requisito}
    
    {context}
    
    Fornisci la tua valutazione in questo formato:
    
    1. **Contesto Generale**
    - [Il contesto generale del requisito (di cosa si tratta, qual è l'obiettivo]
    
    2. **Attori Coinvolti**
    - [I principali attori/utenti coinvolti]

    3. **Scenari**:
    - [Gli scenari d'uso:
           - Scenari principali (flusso normale)
           - Scenari alternativi (flussi alternativi plausibili)
           - Scenari negativi (situazioni in cui qualcosa non funziona)
           - Corner cases (situazioni limite)]
    
    4. **Variabili Dinamiche**
    - [Le variabili dinamiche presenti nel requisito]
    
    ### Flusso di Lavoro:
    [Flusso di lavoro strutturato]

    . **Rispondi solo in italiano, fornisci SOLO la struttura richiesta, senza testo pre e post**
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(wait_time)  # Attendi prima di riprovare
            else:
                raise  # Se raggiunge il massimo dei tentativi, rilancia l'eccezione

def run_analista_rischio(requisiti_analysis, client, model="gemini-2.0-flash-001"):
    prompt = f"""
        **Ruolo:** Sei un Analista di Rischio esperto, incaricato di valutare i rischi associati ai casi d'uso identificati nell'analisi dei requisiti fornita.
        **Obiettivo:** Generare un'analisi dei rischi in formato tabellare, facilmente convertibile in una tabella Markdown.
        **Formato Tabellare Richiesto:**
        ```
        ID|Scenario|Criticità|Fattore di Rischio|Motivazione|Frequenza|Rischio Finale
        ---|---|---|---|---|---|---
        ```
        **Per ogni scenario presente nell'analisi dei requisiti, devi fornire le seguenti informazioni:**
        * **ID:** Un identificatore univoco per il rischio (es. RS001, RS002, ecc.). Assicurati che ogni riga abbia un ID unico.
        * **Scenario:** Una breve descrizione del caso d'uso o della funzionalità a cui si riferisce il rischio. Copia o riassumi lo scenario dall'analisi dei requisiti.
        * **Criticità:** Una descrizione concisa della potenziale conseguenza negativa o del problema che potrebbe verificarsi.
        * **Fattore di Rischio:** Una valutazione qualitativa della probabilità che l'evento critico si verifichi (basso, medio, alto).
        * **Motivazione:** Una breve spiegazione del perché hai assegnato quel particolare fattore di rischio. Considera fattori come la complessità, le dipendenze, la familiarità del team, ecc.
        * **Frequenza:** La frequenza prevista con cui lo scenario o la funzionalità verranno utilizzati (rara, occasionale, frequente).
        * **Rischio Finale:** Una valutazione del rischio complessivo, derivata dalla combinazione della Criticità, del Fattore di Rischio e della Frequenza. Puoi usare una logica semplice (es. Basso + Rara = Basso, Alto + Frequente = Alto) o una tua expertise.
        
        **Importante:**
        * **Rispondi unicamente con la tabella formattata in Markdown**, utilizzando il carattere `|` come separatore di colonne, come mostrato nell'esempio sopra. Non includere alcun altro testo o spiegazione al di fuori della tabella.
        * Assicurati che la tabella sia ben formattata e facilmente parsabile.
        * Analizza attentamente ogni scenario presente nell'analisi dei requisiti fornita.
        
        **Analisi dei Requisiti:**
        {requisiti_analysis}
        """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise

def run_generatore_test(requisiti_analysis, rischio_analysis, client, model="gemini-2.0-flash-001"):
    prompt = f"""
        Sei un Test Engineer esperto. Il tuo compito è generare test case completi basati sull'analisi dei requisiti e sull'analisi del rischio.
        Devi generare i test case in un formato strutturato che possa essere facilmente convertito in una tabella, seguendo questo schema per ogni test case:
        ID|Titolo|Precondizioni|Passi|Risultato Atteso|Scenario|Rischio
        ---|------|------------|-----|---------------|--------|------
        Per ogni test case, specifica:
        - ID univoco del test (es. TC001)
        - Titolo descrittivo
        - Precondizioni
        - Passi da eseguire (separati da punto e virgola)
        - Risultato atteso
        - Scenario coperto
        - Livello di rischio associato (basso, medio, alto)
        Verifica poi che tutti i test case possibili siano stati coperti da almeno un caso di test, e che eventuali corner case abbiano anch'essi dei rispettivi test case.
        Ecco l'analisi dei requisiti:
        {requisiti_analysis}
        Ecco l'analisi del rischio:
        {rischio_analysis}
        **Rispondi solo con la tabella, niente altro** e assicurati che l'output sia formattato come una tabella con il separatore | come mostrato sopra.
        """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise

def run_analizzatore_automazione(test_cases, client, model="gemini-2.0-flash-001"):
    prompt = f"""
        Agisci come un Automation Engineer esperto con una forte mentalità orientata al ROI (Return on Investment). Il tuo compito è analizzare una serie di test case e determinare la loro idoneità all'automazione, considerando attentamente il bilanciamento tra il valore dell'automazione e l'effort necessario per implementarla in termini di tempo e risorse (costo). Suggerisci lo strumento più appropriato (Postman per test API o modifiche dati, Cypress per test end-to-end web, Appium per test end-to-end mobile) e assegna una priorità di automazione, concentrandoti sull'automazione di test **critici e fondamentali per la stabilità e la funzionalità in ambiente di produzione**.
        Identifica come casi da automatizzare solo quelli che in rapporto costi/benefici rappresentano un importante valore aggiunto tale da giustificare la spesa
        Dopo aver identificato i casi, restringili a quelli che si possono ripetere in produzione senza richiedere azioni dispositive (es storni a seguito di pagamenti per fare un test ecc)
        
        Fornisci la tua analisi in un formato tabellare Markdown, seguendo rigorosamente questa struttura:

        ID Test|Titolo Test|Adatto Automazione?|Strumento Consigliato|Priorità Automazione|Stima Effort (Giorni Uomo)|Note Implementazione
        ---|---|---|---|---|---|---

        Per ogni test case fornito, valuta attentamente i seguenti aspetti:
        - ID Test: Riporta l'ID univoco del test case.
        - Titolo Test: Fornisci una breve e chiara descrizione del test.
        - Adatto Automazione?: Indica con "Sì" o "No" se il test è un buon candidato per l'automazione **considerando il rapporto tra il valore dell'automazione (riduzione del rischio in produzione, frequenza di esecuzione, tempo risparmiato a lungo termine) e l'effort stimato per implementarla**. Automatizza solo i test che portano un beneficio significativo in ottica di produzione.
        - Strumento Consigliato: Se "Adatto Automazione?" è "Sì", specifica lo strumento di automazione suggerito tra "Postman", "Cypress", "Appium". Se il test non è adatto, indica "Nessuno".
        - Priorità Automazione: Assegna una priorità all'automazione ("Alta", "Media", "Bassa") basata sull'**importanza del test per la stabilità in produzione, la frequenza di esecuzione e il ROI potenziale**. Concentrati sull'automatizzare con alta priorità i test fondamentali e critici.
        - Stima Effort (Giorni Uomo): Fornisci una stima approssimativa dell'effort necessario per automatizzare completamente il test in termini di giorni uomo. Considera la complessità del test, la familiarità con lo strumento e la necessità di eventuali setup specifici.
        - Note Implementazione: Includi eventuali considerazioni specifiche sull'implementazione dell'automazione per questo test, come prerequisiti, sfide potenziali, strategie particolari o se ci sono alternative all'automazione che potrebbero essere più efficienti.

        **Rispondi unicamente con la tabella Markdown formattata**, senza aggiungere alcun altro testo o spiegazione. Assicurati che la tabella sia ben formattata con il carattere '|' come separatore di colonne.

        Ecco i test case da analizzare:
        {test_cases}
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 5  # Exponential backoff
                print(f"Errore 503. Tentativo {attempt + 1} di {max_retries}. Ritento tra {wait_time} secondi...")
            else:
                raise  # Rilancia l'eccezione se non è un 503 o se ha superato i tentativi

def run_analista_performance(requisiti_analysis, rischio_analysis, client, model="gemini-2.0-flash-001"):
    prompt = f"""
    Sei un Performance Test Engineer esperto. Analizza i requisiti e i rischi per determinare se sono necessari performance test.
    Rispondi in formato tabellare strutturato (usando | come separatore), seguendo ESATTAMENTE questo schema:

    Necessari?|Tipo Test|Metriche Chiave|Soglie Ideali|Utenti Simulati|Note
    ---|------|------------|-----|---------------|--------
    [Sì/No]|[Load/Stress...]|[es. Latenza, Throughput]|[es. soglie ideali per best practice|[es. 100-1000]|[considerazioni aggiuntive]

    IMPORTANTE:
    1. Usa SOLO il formato sopra specificato
    2. Non aggiungere testo prima o dopo la tabella
    3. Assicurati che ogni riga abbia ESATTAMENTE 6 colonne separate da |

    Criteri per raccomandare performance test:
    - Presenza di scenari ad alto traffico (es. pagamenti, login massivi)
    - Requisiti non funzionali espliciti (es. "deve supportare 1000 RPS")
    - Rischio alto di colli di bottiglia (es. database, API esterne)
    - Componenti critici per il business (es. checkout, flussi pagamento)

    Ecco l'analisi dei requisiti:
    {requisiti_analysis}

    Ecco l'analisi del rischio:
    {rischio_analysis}
    """
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text

def jira_integration_page():
    jira = get_jira_instance()
    if not jira:
        st.warning("Impossibile connettersi a Jira.")
        return

    projects = get_jira_projects(jira)
    if not projects:
        st.warning("Impossibile recuperare i progetti Jira.")
        return

    # Utilizza st.columns per creare due colonne
    col1, col2 = st.columns(2)

    with col1:
        selected_project_key = st.selectbox("Seleziona Progetto Jira", options=list(projects.keys()),
                                         format_func=projects.get)
    with col2:
        issue_types = st.multiselect("Seleziona Tipi di Issue", options=["Epic", "Story"], default=["Story"])

    issues = get_project_issues(jira, selected_project_key, issue_types)

    selected_issues = []
    if issues:
        st.subheader("Issue Trovate")

        num_cols = 3  # Numero di colonne desiderato (4 per riga)
        cols = st.columns(num_cols)
        issue_index = 0

        for issue in issues:
            project_name = issue['fields']['project']['name']
            display_text = f"**{issue['key']}** - {issue['fields']['summary']}"

            # Calcola l'indice della colonna
            col_index = issue_index % num_cols
            with cols[col_index]:
                checkbox = st.checkbox(label=display_text, key=issue["key"])
                if checkbox:
                    selected_issues.append(issue)
                # Aggiungi un piccolo expander per i dettagli (opzionale)
                with st.expander("Dettagli", expanded=False):
                    st.write(f" {issue['fields']['description'] if issue['fields']['description'] else 'Nessuna descrizione fornita.'}")

            issue_index += 1
    else:
        st.info("Nessuna issue trovata per i criteri selezionati.")

    if selected_issues:
        st.subheader("Azioni sulle Issue Selezionate")
        if st.button("Esegui Analisi Completa"):
            client = get_genai_client()

            for issue in selected_issues:
                st.subheader(f"Risultati Analisi {issue['key']} - {issue['fields']['summary']}")

                if 'results' not in st.session_state:
                    st.session_state.results = {
                        "ValutatoreRequisiti": "",
                        "AnalistaRequisiti": "",
                        "AnalistaRischio": "",
                        "GeneratoreTest": "",
                        "AnalizzatoreAutomazione": "",
                        "AnalizzatorePerformance": ""
                    }
                if 'requisito' not in st.session_state:
                    st.session_state.requisito = ""

                if issue['fields']['description']:
                    # Esegui gli agenti e visualizza i risultati (come in single_requirement_page)
                    with st.spinner("Esecuzione degli agenti..."):
                        requisito = issue['fields']['description']

                        # Esegui Valutatore Requisiti
                        valutatore_result = run_valutatore_requisiti(requisito, client, model="gemini-2.0-flash-001")
                        st.session_state.results["ValutatoreRequisiti"] = valutatore_result

                        # Esegui Analista Requisiti
                        analista_result = run_analista_requisiti(requisito, client, model="gemini-2.0-flash-001")
                        st.session_state.results["AnalistaRequisiti"] = analista_result

                        # Esegui Analista Rischio
                        analista_rischio_result = run_analista_rischio(analista_result, client, model="gemini-2.0-flash-001")
                        st.session_state.results["AnalistaRischio"] = analista_rischio_result

                        # Esegui Generatore Test
                        generatore_test_result = run_generatore_test(analista_result, analista_rischio_result, client, model="gemini-2.0-flash-001")
                        st.session_state.results["GeneratoreTest"] = generatore_test_result

                        # Esegui Analizzatore Automazione
                        analizzatore_automazione_result = run_analizzatore_automazione(generatore_test_result, client, model="gemini-2.0-flash-001")
                        st.session_state.results["AnalizzatoreAutomazione"] = analizzatore_automazione_result

                        # Esegui Analizzatore Performance
                        analizzatore_performance_result = run_analista_performance(analista_result, analista_rischio_result, client, model="gemini-2.0-flash-001")
                        st.session_state.results["AnalizzatorePerformance"] = analizzatore_performance_result

                    # Visualizza i risultati (ADATTATO DA single_requirement_page)
                    st.markdown("""
                        <style>
                            /* Stili per i box degli elementi in base al tema - VERSIONE ACCESA */
                            @media (prefers-color-scheme: dark) {
                                /* Stili per la dark mode */
                                .dark-mode-present {
                                    background-color: #006400 !important;  /* Verde più acceso */
                                    color: #ffffff !important;
                                    border-left: 4px solid #00FF00;
                                }

                                .dark-mode-missing {
                                    background-color: #8B0000 !important;  /* Rosso più acceso */
                                    color: #ffffff !important;
                                    border-left: 4px solid #FF4500;
                                }

                                .dark-mode-improved {
                                    background-color: #00008B !important;  /* Blu più acceso */
                                    color: #ffffff !important;
                                    border-left: 4px solid #1E90FF;
                                }

                                .dark-mode-notes {
                                    background-color: #8B8000 !important;  /* Giallo/oro più acceso */
                                    color: #ffffff !important;
                                    border-left: 4px solid #FFD700;
                                }
                            }

                            @media (prefers-color-scheme: light) {
                                /* Stili per la light mode */
                                .dark-mode-present {
                                    background-color: #90EE90 !important;  /* Verde chiaro acceso */
                                    color: #006400 !important;
                                    border-left: 4px solid #008000;
                                }

                                .dark-mode-missing {
                                    background-color: #FFA07A !important;  /* Rosso chiaro acceso */
                                    color: #8B0000 !important;
                                    border-left: 4px solid #FF0000;
                                }

                                .dark-mode-improved {
                                    background-color: #ADD8E6 !important;  /* Blu chiaro acceso */
                                    color: #000080 !important;
                                    border-left: 4px solid #0000FF;
                                }

                                .dark-mode-notes {
                                    background-color: #FFFACD !important;  /* Giallo chiaro acceso */
                                    color: #8B8000 !important;
                                    border-left: 4px solid #FFD700;
                                }
                            }

                            /* Stili comuni per i box - AUMENTATO IL PADDING E MARGIN */
                            .element-box {
                                padding: 12px 15px !important;
                                border-radius: 6px !important;
                                margin: 8px 0 !important;
                                font-weight: 500 !important;
                            }
                            /* Classe generale più grande per il box del requisito migliorato */
                            .improved-box {
                                padding: 18px 20px !important;
                                margin-bottom: 25px !important;
                                font-size: 1.05em !important;
                            }
                        </style>
                    """, unsafe_allow_html=True)

                    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "Valutatore Requisiti", "Analista Requisiti", "Analista Rischio",
                        "Generatore Test", "Analizzatore Automazione", "Performance Test"
                    ])

                    with tab0:
                        st.subheader("Valutazione e Miglioramento Requisiti")
                        vr_result = st.session_state.results.get("ValutatoreRequisiti", "")
                        if vr_result:
                            # Funzione per estrarre sezioni
                            def extract_section(content, section_title):
                                start_idx = content.find(f"### {section_title}:")
                                if start_idx == -1:
                                    return ""
                                start_idx += len(f"### {section_title}:") + 1
                                end_idx = content.find("### ", start_idx)
                                if end_idx == -1:
                                    return content[start_idx:].strip()
                                return content[start_idx:end_idx].strip()

                            # Estrai le sezioni
                            completezza = extract_section(vr_result, "Valutazione Completezza")
                            presenti = extract_section(vr_result, "Elementi Presenti")
                            mancanti = extract_section(vr_result, "Elementi Mancanti")
                            migliorato = extract_section(vr_result, "Requisito Migliorato")
                            note = extract_section(vr_result, "Note")

                            # 1. Valutazione di completezza con indicatore visivo
                            st.markdown("### 📊 Valutazione Completezza")
                            if completezza:
                                if "incompleto" not in completezza.lower() and "parzialmente" not in completezza.lower():
                                    st.success(f"✅ {completezza}")
                                elif "parzialmente" in completezza.lower():
                                    st.warning(f"⚠️ {completezza}")
                                else:
                                    st.error(f"❌ {completezza}")
                            else:
                                st.info("Nessuna valutazione di completezza disponibile")

                            # 2. Layout a colonne per elementi presenti/mancanti
                            st.markdown("### 🔍 Elementi Identificati")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("#### ✅ Presenti")
                                if presenti:
                                    present_items = [item.strip()[2:] for item in presenti.split('\n') if item.startswith("- ")]
                                    if present_items:
                                        for item in present_items:
                                            st.markdown(f"""
                                                <div class='element-box dark-mode-present'>
                                                    <strong>✓ {item}</strong>
                                                </div>
                                            """, unsafe_allow_html=True)
                                    else:
                                        st.info("Nessun elemento presente identificato")
                                else:
                                    st.info("Nessuna informazione sugli elementi presenti")
                            with col2:
                                st.markdown("#### ❌ Mancanti")
                                if mancanti:
                                    missing_items = [item.strip()[2:] for item in mancanti.split('\n') if item.startswith("- ")]
                                    if missing_items:
                                        for item in missing_items:
                                            st.markdown(f"""
                                                <div class='element-box dark-mode-missing'>
                                                    <strong>✗ {item}</strong>
                                                </div>
                                            """, unsafe_allow_html=True)
                                    else:
                                        st.success("Tutti gli elementi necessari sono presenti!")
                                else:
                                    st.info("Nessuna informazione sugli elementi mancanti")

                            # 3. Requisito migliorato (sotto gli elementi mancanti)
                            if migliorato:
                                st.markdown("### ✨ Requisito Migliorato")
                                st.markdown(f"""
                                    <div class='element-box improved-box dark-mode-improved'>
                                        <strong>{migliorato}</strong>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.info("Nessuna versione migliorata del requisito disponibile")

                            # 4. Note aggiuntive (alla fine)
                            if note:
                                st.markdown("### 📝 Note Aggiuntive")
                                st.markdown(f"""
                                    <div class='element-box dark-mode-notes'>
                                        <strong>{note}</strong>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.info("Esegui il Valutatore Requisiti per visualizzare l'analisi")
                        else:
                            st.info("Esegui il Valutatore Requisiti per visualizzare l'analisi")
                    with tab1:
                        st.subheader("Analisi dei Requisiti e Scenari")
                        def parse_analisi_requisiti(text):
                            # Lista delle sezioni attese con keyword associate
                            section_keywords = {
                                "contesto": ["contesto", "obiettivo"],
                                "attori": ["attori", "utenti", "coinvolti"],
                                "scenari": ["scenari"],
                                "variabili": ["variabili", "dinamiche"],
                                "flusso": ["flusso di lavoro"]
                            }
                            sezioni = {k: "" for k in section_keywords}
                            lines = text.strip().split('\n')
                            current_key = None
                            for line in lines:
                                line_clean = line.strip().lower()
                                # Cerca se la linea è un'intestazione
                                for key, keywords in section_keywords.items():
                                    if any(kw in line_clean for kw in keywords) and len(line_clean) < 80:
                                        current_key = key
                                        break
                                else:
                                    if current_key:
                                        sezioni[current_key] += line.strip() + "\n"
                            # Sezione vuota fallback
                            for key in sezioni:
                                if not sezioni[key].strip():
                                    sezioni[key] = "Nessun contenuto trovato"
                            return sezioni
                        ar_result = st.session_state.results["AnalistaRequisiti"]
                        if ar_result:
                            sezioni = parse_analisi_requisiti(ar_result)
                            st.markdown("### 🎯 Contesto Generale")
                            st.markdown(sezioni["contesto"] or "*Nessun contenuto trovato*")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("### 👥 Attori Coinvolti")
                                st.markdown(sezioni["attori"] or "*Nessun contenuto trovato*")
                            with col2:
                                st.markdown("### ⚙️ Variabili Dinamiche")
                                st.markdown(sezioni["variabili"] or "*Nessun contenuto trovato*")
                            col3, col4 = st.columns(2)
                            with col3:
                                st.markdown("### 🎬 Scenari d'Uso")
                                st.markdown(sezioni["scenari"] or "*Nessun contenuto trovato*")
                            with col4:
                                st.markdown("### 🛤️ Flusso di Lavoro")
                                st.markdown(sezioni["flusso"] or "*Nessun contenuto trovato*")
                        else:
                            st.info("Esegui l'Analista dei Requisiti per visualizzare l'analisi")
               
                    with tab2:
                        st.subheader("Analisi dei Rischi")
                        res = st.session_state.results["AnalistaRischio"]
                        if res:
                            try:
                                # Dividi il risultato in linee
                                lines = res.strip().split('\n')
                                
                                # Estrai l'header (prima linea valida)
                                header = None
                                data_lines = []
                                separator_line = False
                                
                                for line in lines:
                                    if line.strip().startswith('---'):
                                        separator_line = True
                                        continue
                                    if '|' in line:
                                        if not header and not separator_line:
                                            header = [h.strip() for h in line.split('|')]
                                        elif header and separator_line:
                                            data_lines.append([cell.strip() for cell in line.split('|')])
                                
                                if header and data_lines:
                                    # Crea DataFrame
                                    df = pd.DataFrame(data_lines, columns=header)
                                    st.dataframe(df)
                                else:
                                    st.warning("Formato tabella non riconosciuto.")
                                    st.text(res)
                            except Exception as e:
                                st.error(f"Errore durante l'elaborazione della tabella: {e}")
                                st.text(res)
                        else:
                            st.info("Esegui l'analisi per visualizzare l'analisi dei rischi.")

                    with tab3:
                        st.subheader("Generazione Test Case")
                        res = st.session_state.results["GeneratoreTest"]
                        if res:
                            try:
                                # Stessa logica di parsing del tab2
                                lines = res.strip().split('\n')
                                header = None
                                data_lines = []
                                separator_line = False
                                
                                for line in lines:
                                    if line.strip().startswith('---'):
                                        separator_line = True
                                        continue
                                    if '|' in line:
                                        if not header and not separator_line:
                                            header = [h.strip() for h in line.split('|')]
                                        elif header and separator_line:
                                            data_lines.append([cell.strip() for cell in line.split('|')])
                                
                                if header and data_lines:
                                    df = pd.DataFrame(data_lines, columns=header)
                                    st.dataframe(df)
                                else:
                                    st.warning("Formato tabella non riconosciuto.")
                                    st.text(res)
                            except Exception as e:
                                st.error(f"Errore durante l'elaborazione della tabella: {e}")
                                st.text(res)
                        else:
                            st.info("Esegui l'analisi per visualizzare i test case generati.")

                    with tab4:
                        st.subheader("Analisi Automazione")
                        res = st.session_state.results["AnalizzatoreAutomazione"]
                        if res:
                            try:
                                # Stessa logica di parsing del tab2
                                lines = res.strip().split('\n')
                                header = None
                                data_lines = []
                                separator_line = False
                                
                                for line in lines:
                                    if line.strip().startswith('---'):
                                        separator_line = True
                                        continue
                                    if '|' in line:
                                        if not header and not separator_line:
                                            header = [h.strip() for h in line.split('|')]
                                        elif header and separator_line:
                                            data_lines.append([cell.strip() for cell in line.split('|')])
                                
                                if header and data_lines:
                                    df = pd.DataFrame(data_lines, columns=header)
                                    st.dataframe(df)
                                else:
                                    st.warning("Formato tabella non riconosciuto.")
                                    st.text(res)
                            except Exception as e:
                                st.error(f"Errore durante l'elaborazione della tabella: {e}")
                                st.text(res)
                        else:
                            st.info("Esegui l'analisi per visualizzare l'analisi di automazione.")

                    with tab5:
                        st.subheader("Analisi Performance")
                        res = st.session_state.results["AnalizzatorePerformance"]
                        if res:
                            try:
                                # Stessa logica di parsing del tab2
                                lines = res.strip().split('\n')
                                header = None
                                data_lines = []
                                separator_line = False
                                
                                for line in lines:
                                    if line.strip().startswith('---'):
                                        separator_line = True
                                        continue
                                    if '|' in line:
                                        if not header and not separator_line:
                                            header = [h.strip() for h in line.split('|')]
                                        elif header and separator_line:
                                            data_lines.append([cell.strip() for cell in line.split('|')])
                                
                                if header and data_lines:
                                    df = pd.DataFrame(data_lines, columns=header)
                                    st.dataframe(df)
                                else:
                                    st.warning("Formato tabella non riconosciuto.")
                                    st.text(res)
                            except Exception as e:
                                st.error(f"Errore durante l'elaborazione della tabella: {e}")
                                st.text(res)
                        else:
                            st.info("Esegui l'analisi per visualizzare l'analisi di Perfomance.")

def single_requirement_page():
    # Sostituisci la parte CSS relativa ai colori dei box nel tab 0 con questo:
    st.markdown("""
    <style>
        /* Stili per i box degli elementi in base al tema - VERSIONE ACCESA */
        @media (prefers-color-scheme: dark) {
            /* Stili per la dark mode */
            .dark-mode-present {
                background-color: #006400 !important;  /* Verde più acceso */
                color: #ffffff !important;
                border-left: 4px solid #00FF00;
            }
            
            .dark-mode-missing {
                background-color: #8B0000 !important;  /* Rosso più acceso */
                color: #ffffff !important;
                border-left: 4px solid #FF4500;
            }
            
            .dark-mode-improved {
                background-color: #00008B !important;  /* Blu più acceso */
                color: #ffffff !important;
                border-left: 4px solid #1E90FF;
            }
            
            .dark-mode-notes {
                background-color: #8B8000 !important;  /* Giallo/oro più acceso */
                color: #ffffff !important;
                border-left: 4px solid #FFD700;
            }
        }
        
        @media (prefers-color-scheme: light) {
            /* Stili per la light mode */
            .dark-mode-present {
                background-color: #90EE90 !important;  /* Verde chiaro acceso */
                color: #006400 !important;
                border-left: 4px solid #008000;
            }
            
            .dark-mode-missing {
                background-color: #FFA07A !important;  /* Rosso chiaro acceso */
                color: #8B0000 !important;
                border-left: 4px solid #FF0000;
            }
            
            .dark-mode-improved {
                background-color: #ADD8E6 !important;  /* Blu chiaro acceso */
                color: #000080 !important;
                border-left: 4px solid #0000FF;
            }
            
            .dark-mode-notes {
                background-color: #FFFACD !important;  /* Giallo chiaro acceso */
                color: #8B8000 !important;
                border-left: 4px solid #FFD700;
            }
        }
        
        /* Stili comuni per i box - AUMENTATO IL PADDING E MARGIN */
        .element-box {
            padding: 12px 15px !important; 
            border-radius: 6px !important; 
            margin: 8px 0 !important;
            font-weight: 500 !important;
        }
        
        /* Classe generale più grande per il box del requisito migliorato */
        .improved-box {
            padding: 18px 20px !important;
            margin-bottom: 25px !important;
            font-size: 1.05em !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Inizializza lo stato della sessione - AGGIUNTA LA CHIAVE "ValutatoreRequisiti"
    if 'results' not in st.session_state:
        st.session_state.results = {
            "ValutatoreRequisiti": "",  # Aggiunto questo
            "AnalistaRequisiti": "",
            "AnalistaRischio": "",
            "GeneratoreTest": "",
            "AnalizzatoreAutomazione": ""
        }
    
    if 'requisito' not in st.session_state:
        st.session_state.requisito = ""
    
    # Client Google AI (viene creato una sola volta)
    client = get_genai_client()
    
    # Sidebar per i controlli
    with st.sidebar:
        st.header("Controlli")
        model_selection = st.selectbox(
            "Seleziona modello:",
            ["gemini-2.0-flash-001", "gemini-2.0-pro-001"],
            index=0
        )
        if st.button("Pulisci Tutto"):
            st.session_state.results = {
                "ValutatoreRequisiti": "",  # Aggiunto questo
                "AnalistaRequisiti": "",
                "AnalistaRischio": "",
                "GeneratoreTest": "",
                "AnalizzatoreAutomazione": ""
            }
            st.session_state.requisito = ""
            st.rerun()
    
    # Area input requisito
    st.text_area("Inserisci il requisito:", key="requisito", height=80)
    
    # Aggiungi un nuovo tab accanto agli altri
    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Valutatore Requisiti", 
        "Analista Requisiti", 
        "Analista Rischio", 
        "Generatore Test", 
        "Analizzatore Automazione",
        "Performance Test",
    ])
    
    with tab0:
        st.subheader("Valutazione e Miglioramento Requisiti")
        if st.button("Esegui Valutatore Requisiti"):
            if not st.session_state.requisito:
                st.warning("Inserisci un requisito prima di eseguire la valutazione")
            else:
                with st.spinner("Valutazione requisito in corso..."):
                    result = run_valutatore_requisiti(st.session_state.requisito, client, model=model_selection)
                    st.session_state.results["ValutatoreRequisiti"] = result
        
        vr_result = st.session_state.results.get("ValutatoreRequisiti", "")
        
        if vr_result:
            # Funzione per estrarre sezioni
            def extract_section(content, section_title):
                start_idx = content.find(f"### {section_title}:")
                if start_idx == -1:
                    return ""
                
                start_idx += len(f"### {section_title}:") + 1
                end_idx = content.find("### ", start_idx)
                if end_idx == -1:
                    return content[start_idx:].strip()
                return content[start_idx:end_idx].strip()
            
            # Estrai le sezioni
            completezza = extract_section(vr_result, "Valutazione Completezza")
            presenti = extract_section(vr_result, "Elementi Presenti")
            mancanti = extract_section(vr_result, "Elementi Mancanti")
            migliorato = extract_section(vr_result, "Requisito Migliorato")
            note = extract_section(vr_result, "Note")
            
            # 1. Valutazione di completezza con indicatore visivo
            st.markdown("### 📊 Valutazione Completezza")
            if completezza:
                if "incompleto" not in completezza.lower() and "parzialmente" not in completezza.lower():
                    st.success(f"✅ {completezza}")
                elif "parzialmente" in completezza.lower():
                    st.warning(f"⚠️ {completezza}")
                else:
                    st.error(f"❌ {completezza}")
            else:
                st.info("Nessuna valutazione di completezza disponibile")
            
            # 2. Layout a colonne per elementi presenti/mancanti
            st.markdown("### 🔍 Elementi Identificati")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ✅ Presenti")
                if presenti:
                    present_items = [item.strip()[2:] for item in presenti.split('\n') if item.startswith("- ")]
                    if present_items:
                        for item in present_items:
                            st.markdown(f"""
                            <div class='element-box dark-mode-present'>
                            <strong>✓ {item}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Nessun elemento presente identificato")
                else:
                    st.info("Nessuna informazione sugli elementi presenti")
            
            with col2:
                st.markdown("#### ❌ Mancanti")
                if mancanti:
                    missing_items = [item.strip()[2:] for item in mancanti.split('\n') if item.startswith("- ")]
                    if missing_items:
                        for item in missing_items:
                            st.markdown(f"""
                            <div class='element-box dark-mode-missing'>
                            <strong>✗ {item}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("Tutti gli elementi necessari sono presenti!")
                else:
                    st.info("Nessuna informazione sugli elementi mancanti")
            
            # 3. Requisito migliorato (sotto gli elementi mancanti)
            if migliorato:
                st.markdown("### ✨ Requisito Migliorato")
                st.markdown(f"""
                <div class='element-box improved-box dark-mode-improved'>
                <strong>{migliorato}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Nessuna versione migliorata del requisito disponibile")
            
            # 4. Note aggiuntive (alla fine)
            if note:
                st.markdown("### 📝 Note Aggiuntive")
                st.markdown(f"""
                <div class='element-box dark-mode-notes'>
                <strong>{note}</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Esegui il Valutatore Requisiti per visualizzare l'analisi")


    with tab1:
        st.subheader("Analisi dei Requisiti e Scenari")

        def parse_analisi_requisiti(text):
            # Lista delle sezioni attese con keyword associate
            section_keywords = {
                "contesto": ["contesto", "obiettivo"],
                "attori": ["attori", "utenti", "coinvolti"],
                "scenari": ["scenari"],
                "variabili": ["variabili", "dinamiche"],
                "flusso": ["flusso di lavoro"]
            }

            sezioni = {k: "" for k in section_keywords}

            lines = text.strip().split('\n')
            current_key = None

            for line in lines:
                line_clean = line.strip().lower()

                # Cerca se la linea è un'intestazione
                for key, keywords in section_keywords.items():
                    if any(kw in line_clean for kw in keywords) and len(line_clean) < 80:
                        current_key = key
                        break
                else:
                    if current_key:
                        sezioni[current_key] += line.strip() + "\n"

            # Sezione vuota fallback
            for key in sezioni:
                if not sezioni[key].strip():
                    sezioni[key] = "Nessun contenuto trovato"

            return sezioni

        if st.button("Esegui Analista Requisiti"):
            if not st.session_state.requisito:
                st.warning("Inserisci un requisito prima di eseguire l'analisi")
            else:
                with st.spinner("Analisi in corso..."):
                    requisito_da_analizzare = st.session_state.results["ValutatoreRequisiti"] or st.session_state.requisito
                    result = run_analista_requisiti(requisito_da_analizzare, client, model=model_selection)
                    st.session_state.results["AnalistaRequisiti"] = result

        ar_result = st.session_state.results["AnalistaRequisiti"]

        if ar_result:
                            sezioni = parse_analisi_requisiti(ar_result)
                            st.markdown("### 🎯 Contesto Generale")
                            st.markdown(sezioni["contesto"] or "*Nessun contenuto trovato*")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("### 👥 Attori Coinvolti")
                                st.markdown(sezioni["attori"] or "*Nessun contenuto trovato*")
                            with col2:
                                st.markdown("### ⚙️ Variabili Dinamiche")
                                st.markdown(sezioni["variabili"] or "*Nessun contenuto trovato*")
                            col3, col4 = st.columns(2)
                            with col3:
                                st.markdown("### 🎬 Scenari d'Uso")
                                st.markdown(sezioni["scenari"] or "*Nessun contenuto trovato*")
                            with col4:
                                st.markdown("### 🛤️ Flusso di Lavoro")
                                st.markdown(sezioni["flusso"] or "*Nessun contenuto trovato*")

    # Tab Analista Rischio
    with tab2:
        st.subheader("Analisi del Rischio")
        if st.button("Esegui Analista Rischio"):
            if not st.session_state.results["AnalistaRequisiti"]:
                st.warning("Esegui prima l'Analista Requisiti")
            else:
                with st.spinner("Analisi del rischio in corso..."):
                    result = run_analista_rischio(st.session_state.results["AnalistaRequisiti"], client, model=model_selection)
                    st.session_state.results["AnalistaRischio"] = result

        # Visualizzazione dei risultati
        if st.session_state.results["AnalistaRischio"]:
            # Dividi il risultato in linee
            lines = st.session_state.results["AnalistaRischio"].strip().split('\n')
            
            # Estrai l'header (prima linea)
            headers = [h.strip() for h in lines[1].split('|')]
            
            # Estrai i dati (tutte le linee successive) e filtra le righe
            data = []
            for line in lines[3:]:  # Salta la prima linea (header) e la seconda (separatore)
                if line.strip():  # Ignora linee vuote
                    row = [d.strip().replace(';', ';\n') for d in line.split('|')]
                    # Verifica se ci sono celle vuote o con "None" nella riga
                    if not any(not cell or cell.lower() == '```' for cell in row):
                        data.append(row)
            
            # Crea un DataFrame pandas per visualizzazione
            df = pd.DataFrame(data, columns=headers)
            
            # Visualizza la tabella con gli header corretti
            st.dataframe(df)
        else:
            st.info("Esegui l'Analista Rischio per visualizzare i risultati")
    
    # Tab Generatore Test
    with tab3:
        st.subheader("Generazione Test Case")
        if st.button("Esegui Generatore Test"):
            if not st.session_state.results["AnalistaRequisiti"] or not st.session_state.results["AnalistaRischio"]:
                st.warning("Esegui prima l'Analista Requisiti e l'Analista Rischio")
            else:
                with st.spinner("Generazione test case in corso..."):
                    result = run_generatore_test(
                        st.session_state.results["AnalistaRequisiti"],
                        st.session_state.results["AnalistaRischio"],
                        client,
                        model=model_selection
                    )
                    st.session_state.results["GeneratoreTest"] = result

        # Visualizzazione dei risultati
        if st.session_state.results["GeneratoreTest"]:
            # Dividi il risultato in linee
            lines = st.session_state.results["GeneratoreTest"].strip().split('\n')

            # Estrai l'header (prima linea)
            headers = [h.strip() for h in lines[1].split('|')]

            # Estrai i dati (tutte le linee successive) e filtra le righe
            data = []
            for line in lines[3:]:  # Salta la prima linea (header) e la seconda (separatore)
                if line.strip():  # Ignora linee vuote
                    row = [d.strip().replace(';', ';\n') for d in line.split('|')]
                    # Verifica se ci sono celle vuote o con "None" nella riga
                    if not any(not cell or cell.lower() == '```' for cell in row):
                        data.append(row)

            # Crea un DataFrame pandas per visualizzazione
            df = pd.DataFrame(data, columns=headers)

            # Visualizza la tabella con gli header corretti
            st.dataframe(df)
        else:
            st.info("Esegui il Generatore Test per visualizzare i risultati")
    
    # Tab Analizzatore Automazione
    with tab4:
        st.subheader("Analisi Automazione")
        if st.button("Esegui Analizzatore Automazione"):
            if not st.session_state.results["GeneratoreTest"]:
                st.warning("Esegui prima il Generatore Test")
            else:
                with st.spinner("Analisi automazione in corso..."):
                    result = run_analizzatore_automazione(st.session_state.results["GeneratoreTest"], client, model=model_selection)
                    st.session_state.results["AnalizzatoreAutomazione"] = result

        # Visualizzazione dei risultati
        if st.session_state.results["AnalizzatoreAutomazione"]:
            # Dividi il risultato in linee
            lines = st.session_state.results["AnalizzatoreAutomazione"].strip().split('\n')
            
            # Estrai l'header (prima linea)
            headers = [h.strip() for h in lines[1].split('|')]
            
            # Estrai i dati (tutte le linee successive) e filtra le righe
            data = []
            for line in lines[3:]:  # Salta la prima linea (header) e la seconda (separatore)
                if line.strip():  # Ignora linee vuote
                    row = [d.strip().replace(';', ';\n') for d in line.split('|')]
                    # Verifica se ci sono celle vuote o con "None" nella riga
                    if not any(not cell or cell.lower() == '```' for cell in row):
                        data.append(row)
            
            # Crea un DataFrame pandas per visualizzazione
            df = pd.DataFrame(data, columns=headers)
            
            # Visualizza la tabella con gli header corretti
            st.dataframe(df)
        
        else:
            st.info("Esegui l'Analizzatore Automazione per visualizzare i risultati")

    # Modifica anche la parte di visualizzazione nel tab:
    with tab5:
        st.subheader("Analisi Performance Test")
        if st.button("Valuta Performance Test"):
            if not st.session_state.results.get("AnalistaRequisiti"):
                st.warning("Esegui prima l'Analista Requisiti")
            else:
                with st.spinner("Analisi performance in corso..."):
                    result = run_analista_performance(
                        st.session_state.results["AnalistaRequisiti"],
                        st.session_state.results.get("AnalistaRischio", ""),
                        client,
                        model=model_selection
                    )
                    st.session_state.results["AnalistaPerformance"] = result

        if st.session_state.results.get("AnalistaPerformance"):
            try:
                # Pulizia e preparazione dei dati
                lines = [line.strip() for line in st.session_state.results["AnalistaPerformance"].split('\n') if line.strip()]
                
                # Estrazione delle colonne (prima riga valida dopo eventuali header)
                header = None
                data_lines = []
                
                for line in lines:
                    if line.startswith("Necessari?|"):
                        header = [h.strip() for h in line.split('|')]
                    elif line.startswith("---|"):
                        continue
                    elif header and '|' in line:
                        data_lines.append([cell.strip() for cell in line.split('|')])
                
                if header and data_lines:
                    # Verifica che tutte le righe abbiano lo stesso numero di colonne dell'header
                    valid_data = []
                    for row in data_lines:
                        if len(row) == len(header):
                            valid_data.append(row)
                    
                    if valid_data:
                        df = pd.DataFrame(valid_data, columns=header)
                        st.dataframe(df)
                    else:
                        st.error("Formattazione dati non valida. Nessuna riga con il numero corretto di colonne.")
                        st.text(st.session_state.results["AnalistaPerformance"])
                else:
                    st.error("Formato tabella non riconosciuto nell'output.")
                    st.text(st.session_state.results["AnalistaPerformance"])
                    
            except Exception as e:
                st.error(f"Errore durante l'elaborazione dei risultati: {str(e)}")
                st.text("Output completo:")
                st.text(st.session_state.results["AnalistaPerformance"])
        else:
            st.info("Esegui l'analisi per valutare i performance test necessari")
    
    if st.button("Esegui Analisi Completa"):
        if not st.session_state.requisito:
            st.warning("Inserisci un requisito prima di eseguire l'analisi")
        else:
            with st.spinner("Analisi completa in corso..."):
                # Valutatore Requisiti
                result = run_valutatore_requisiti(st.session_state.requisito, client, model=model_selection)
                st.session_state.results["ValutatoreRequisiti"] = result
                
                # Analista Requisiti
                requisito_da_analizzare = st.session_state.requisito
                result = run_analista_requisiti(requisito_da_analizzare, client, model=model_selection)
                st.session_state.results["AnalistaRequisiti"] = result
                
                # Analista Rischio
                result = run_analista_rischio(st.session_state.results["AnalistaRequisiti"], client, model=model_selection)
                st.session_state.results["AnalistaRischio"] = result
                
                # Generatore Test
                result = run_generatore_test(
                    st.session_state.results["AnalistaRequisiti"],
                    st.session_state.results["AnalistaRischio"],
                    client,
                    model=model_selection
                )
                st.session_state.results["GeneratoreTest"] = result
                
                # Analizzatore Automazione
                result = run_analizzatore_automazione(st.session_state.results["GeneratoreTest"], client, model=model_selection)
                st.session_state.results["AnalizzatoreAutomazione"] = result
                
                # Analista Performance (NUOVO) 
                result = run_analista_performance(
                    st.session_state.results["AnalistaRequisiti"],
                    st.session_state.results["AnalistaRischio"],
                    client,
                    model=model_selection
                )
                st.session_state.results["AnalistaPerformance"] = result

                # Forza il refresh della pagina per mostrare i nuovi risultati
                st.rerun()
                
def multiple_requirements_page():
    # Inizializza lo stato della sessione per i multi-requisiti
    if 'multi_requirements' not in st.session_state:
        st.session_state.multi_requirements = [""]
    
    if 'multi_results' not in st.session_state:
        st.session_state.multi_results = {
            "ValutatoreRequisiti": [],
            "AnalistaRequisiti": [],
            "AnalistaRischio": [],
            "GeneratoreTest": [],
            "AnalizzatoreAutomazione": [],
            "AnalistaPerformance": []
        }
    
    # Client Google AI
    client = get_genai_client()
    
    # Sidebar per i controlli
    with st.sidebar:
        st.header("Controlli")
        model_selection = st.selectbox(
            "Seleziona modello:",
            ["gemini-2.0-flash-001", "gemini-2.0-pro-001"],
            index=0,
            key="multi_model"
        )
        if st.button("Pulisci Tutto", key="multi_clear"):
            st.session_state.multi_requirements = [""]
            st.session_state.multi_results = {
                "ValutatoreRequisiti": [],
                "AnalistaRequisiti": [],
                "AnalistaRischio": [],
                "GeneratoreTest": [],
                "AnalizzatoreAutomazione": [],
                "AnalistaPerformance": []
            }
            st.rerun()
    
    # Area input multi-requisiti
    st.subheader("Inserisci i Requisiti")
    
    # Funzione per aggiungere un nuovo campo di input
    def add_requirement():
        st.session_state.multi_requirements.append("")
    
    # Funzione per rimuovere un campo di input
    def remove_requirement(index):
        if len(st.session_state.multi_requirements) > 1:
            st.session_state.multi_requirements.pop(index)
    
    # Mostra i campi di input esistenti
    for i, req in enumerate(st.session_state.multi_requirements):
        cols = st.columns([10, 1])
        with cols[0]:
            st.text_area(
                f"Requisito {i+1}", 
                value=req, 
                key=f"multi_req_{i}",
                height=80,
                on_change=lambda i=i: update_requirement(i),
                args=(i,))
        with cols[1]:
            st.button("❌", key=f"remove_{i}", on_click=remove_requirement, args=(i,))
    
    # Pulsante per aggiungere un nuovo requisito
    st.button("➕ Aggiungi Requisito", on_click=add_requirement)
    
    # Funzione per aggiornare un requisito
    def update_requirement(index):
        st.session_state.multi_requirements[index] = st.session_state[f"multi_req_{index}"]
    
    # Pulsante per eseguire l'analisi completa
    if st.button("Esegui Analisi Completa per Tutti i Requisiti"):
        if not any(st.session_state.multi_requirements):
            st.warning("Inserisci almeno un requisito prima di eseguire l'analisi")
        else:
            with st.spinner("Analisi completa in corso per tutti i requisiti..."):
                # Reset dei risultati precedenti
                st.session_state.multi_results = {
                    "ValutatoreRequisiti": [],
                    "AnalistaRequisiti": [],
                    "AnalistaRischio": [],
                    "GeneratoreTest": [],
                    "AnalizzatoreAutomazione": [],
                    "AnalistaPerformance": []
                }
                
                # Esegui l'analisi per ogni requisito
                for req in st.session_state.multi_requirements:
                    if req.strip():  # Solo se il requisito non è vuoto
                        # Valutatore Requisiti
                        vr_result = run_valutatore_requisiti(req, client, model=model_selection)
                        st.session_state.multi_results["ValutatoreRequisiti"].append(vr_result)
                        
                        # Analista Requisiti
                        ar_result = run_analista_requisiti(req, client, model=model_selection)
                        st.session_state.multi_results["AnalistaRequisiti"].append(ar_result)
                        
                        # Analista Rischio
                        risco_result = run_analista_rischio(ar_result, client, model=model_selection)
                        st.session_state.multi_results["AnalistaRischio"].append(risco_result)
                        
                        # Generatore Test
                        gt_result = run_generatore_test(ar_result, risco_result, client, model=model_selection)
                        st.session_state.multi_results["GeneratoreTest"].append(gt_result)
                        
                        # Analizzatore Automazione
                        aa_result = run_analizzatore_automazione(gt_result, client, model=model_selection)
                        st.session_state.multi_results["AnalizzatoreAutomazione"].append(aa_result)
                        
                        # Analista Performance
                        ap_result = run_analista_performance(ar_result, risco_result, client, model=model_selection)
                        st.session_state.multi_results["AnalistaPerformance"].append(ap_result)
                
                st.rerun()
    
    # Mostra i risultati aggregati
    if any(st.session_state.multi_results["ValutatoreRequisiti"]):
        st.subheader("Risultati Aggregati")
        
        # Tab per navigare tra i diversi tipi di risultati
        tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Valutatore Requisiti", 
            "Analista Requisiti", 
            "Analista Rischio", 
            "Generatore Test", 
            "Analizzatore Automazione",
            "Performance Test"
        ])
        
        with tab0:
            st.subheader("Valutazioni Requisiti Aggregati")
            for i, (req, res) in enumerate(zip(st.session_state.multi_requirements, st.session_state.multi_results["ValutatoreRequisiti"])):
                if req.strip():
                    with st.expander(f"Requisito {i+1}: {req[:50]}..."):
                        # Copia e incolla la logica di visualizzazione dalla single_requirement_page
                        # Adatta le key degli elementi di sessione se necessario (es. aggiungi un prefisso)

                        # Funzione per estrarre sezioni (come nella single_requirement_page)
                        def extract_section(content, section_title):
                            start_idx = content.find(f"### {section_title}:")
                            if start_idx == -1:
                                return ""
                            start_idx += len(f"### {section_title}:") + 1
                            end_idx = content.find("### ", start_idx)
                            if end_idx == -1:
                                return content[start_idx:].strip()
                            return content[start_idx:end_idx].strip()

                        # Estrai le sezioni
                        completezza = extract_section(res, "Valutazione Completezza")
                        presenti = extract_section(res, "Elementi Presenti")
                        mancanti = extract_section(res, "Elementi Mancanti")
                        migliorato = extract_section(res, "Requisito Migliorato")
                        note = extract_section(res, "Note")

                        # 1. Valutazione di completezza con indicatore visivo
                        st.markdown("### 📊 Valutazione Completezza")
                        if completezza:
                            if "incompleto" not in completezza.lower() and "parzialmente" not in completezza.lower():
                                st.success(f"✅ {completezza}")
                            elif "parzialmente" in completezza.lower():
                                st.warning(f"⚠️ {completezza}")
                            else:
                                st.error(f"❌ {completezza}")
                        else:
                            st.info("Nessuna valutazione di completezza disponibile")

                        # 2. Layout a colonne per elementi presenti/mancanti
                        st.markdown("### 🔍 Elementi Identificati")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### ✅ Presenti")
                            if presenti:
                                present_items = [item.strip()[2:] for item in presenti.split('\n') if item.startswith("- ")]
                                if present_items:
                                    for item in present_items:
                                        st.markdown(f"""
                                        <div class='element-box dark-mode-present'>
                                        <strong>✓ {item}</strong>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info("Nessun elemento presente identificato")
                            else:
                                st.info("Nessuna informazione sugli elementi presenti")

                        with col2:
                            st.markdown("#### ❌ Mancanti")
                            if mancanti:
                                missing_items = [item.strip()[2:] for item in mancanti.split('\n') if item.startswith("- ")]
                                if missing_items:
                                    for item in missing_items:
                                        st.markdown(f"""
                                        <div class='element-box dark-mode-missing'>
                                        <strong>✗ {item}</strong>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.success("Tutti gli elementi necessari sono presenti!")
                            else:
                                st.info("Nessuna informazione sugli elementi mancanti")

                        # 3. Requisito migliorato (sotto gli elementi mancanti)
                        if migliorato:
                            st.markdown("### ✨ Requisito Migliorato")
                            st.markdown(f"""
                            <div class='element-box improved-box dark-mode-improved'>
                            <strong>{migliorato}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("Nessuna versione migliorata del requisito disponibile")

                        # 4. Note aggiuntive (alla fine)
                        if note:
                            st.markdown("### 📝 Note Aggiuntive")
                            st.markdown(f"""
                            <div class='element-box dark-mode-notes'>
                            <strong>{note}</strong>
                            </div>
                            """, unsafe_allow_html=True)


        with tab1:
            st.subheader("Analisi Requisiti Aggregate")
            for i, (req, res) in enumerate(zip(st.session_state.multi_requirements, st.session_state.multi_results["AnalistaRequisiti"])):
                if req.strip():
                    with st.expander(f"Analisi Requisito {i+1}: {req[:50]}..."):
                        # Copia e incolla la logica di visualizzazione dalla single_requirement_page per l'AnalistaRequisiti
                        # Adatta le key degli elementi di sessione se necessario
                        def parse_analisi_requisiti(text):
                            # Lista delle sezioni attese con keyword associate
                            section_keywords = {
                                "contesto": ["contesto", "obiettivo"],
                                "attori": ["attori", "utenti", "coinvolti"],
                                "scenari": ["scenari"],
                                "variabili": ["variabili", "dinamiche"],
                                "flusso": ["flusso di lavoro"]
                            }

                            sezioni = {k: "" for k in section_keywords}

                            lines = text.strip().split('\n')
                            current_key = None

                            for line in lines:
                                line_clean = line.strip().lower()

                                # Cerca se la linea è un'intestazione
                                for key, keywords in section_keywords.items():
                                    if any(kw in line_clean for kw in keywords) and len(line_clean) < 80:
                                        current_key = key
                                        break
                                else:
                                    if current_key:
                                        sezioni[current_key] += line.strip() + "\n"

                            # Sezione vuota fallback
                            for key in sezioni:
                                if not sezioni[key].strip():
                                    sezioni[key] = "Nessun contenuto trovato"

                            return sezioni

                        sezioni = parse_analisi_requisiti(res)
                        st.markdown("### 🎯 Contesto Generale")
                        st.markdown(sezioni["contesto"] or "*Nessun contenuto trovato*")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("### 👥 Attori Coinvolti")
                            st.markdown(sezioni["attori"] or "*Nessun contenuto trovato*")

                        with col2:
                            st.markdown("### 🔀 Variabili Dinamiche")
                            st.markdown(sezioni["variabili"] or "*Nessun contenuto trovato*")

                        col3, col4 = st.columns(2)

                        with col3:
                            st.markdown("### 📜 Scenari")
                            st.markdown(sezioni["scenari"] or "*Nessun contenuto trovato*")

                        with col4:
                            st.markdown("### 🔄 Flusso di Lavoro")
                            st.markdown(sezioni["flusso"] or "*Nessun contenuto trovato*")

                        # Mostra l'output completo direttamente (senza un altro expander)
                        st.subheader("🔍 Output Completo")
                        st.text_area("Output completo:", value=res, height=400, key=f"ar_result_full_{i}") # Usa una key univoca

        with tab2:
                    st.subheader("Analisi Rischio Aggregate")
                    for i, (req, res) in enumerate(zip(st.session_state.multi_requirements, st.session_state.multi_results["AnalistaRischio"])):
                        if req.strip():
                            with st.expander(f"Rischi Requisito {i+1}: {req[:50]}..."):
                                # Copia e incolla la logica di visualizzazione della tabella dalla single_requirement_page per AnalistaRischio
                                # Adatta le key degli elementi di sessione
                                # Visualizzazione dei risultati
                                if res:
                                    # Dividi il risultato in linee
                                    lines = res.strip().split('\n')

                                    # Estrai l'header (prima linea)
                                    headers = [h.strip() for h in lines[1].split('|')]

                                    # Estrai i dati (tutte le linee successive) e filtra le righe
                                    data = []
                                    for line in lines[3:]:  # Salta la prima linea (header) e la seconda (separatore)
                                        if line.strip():  # Ignora linee vuote
                                            row = [d.strip().replace(';', ';\n') for d in line.split('|')]
                                            # Verifica se ci sono celle vuote o con "None" nella riga
                                            if not any(not cell or cell.lower() == '```' for cell in row):
                                                data.append(row)

                                    # Crea un DataFrame pandas per visualizzazione
                                    df = pd.DataFrame(data, columns=headers)

                                    # Visualizza la tabella con gli header corretti
                                    st.dataframe(df)

                                else:
                                    st.info("Esegui l'Analista Rischio per visualizzare i risultati")

        with tab3:
            st.subheader("Test Case Generati")
            for i, (req, res) in enumerate(zip(st.session_state.multi_requirements, st.session_state.multi_results["GeneratoreTest"])):
                if req.strip():
                    with st.expander(f"Test Requisito {i+1}: {req[:50]}..."):
                        # Copia e incolla la logica di visualizzazione della tabella dalla single_requirement_page per GeneratoreTest
                        # Adatta le key degli elementi di sessione
                        # Visualizzazione dei risultati
                        if res:
                            # Dividi il risultato in linee
                            lines = res.strip().split('\n')

                            # Estrai l'header (prima linea)
                            headers = [h.strip() for h in lines[1].split('|')]

                            # Estrai i dati (tutte le linee successive) e filtra le righe
                            data = []
                            for line in lines[3:]:  # Salta la prima linea (header) e la seconda (separatore)
                                if line.strip():  # Ignora linee vuote
                                    row = [d.strip().replace(';', ';\n') for d in line.split('|')]
                                    # Verifica se ci sono celle vuote o con "None" nella riga
                                    if not any(not cell or cell.lower() == '```' for cell in row):
                                        data.append(row)

                            # Crea un DataFrame pandas per visualizzazione
                            df = pd.DataFrame(data, columns=headers)

                            # Visualizza la tabella con gli header corretti
                            st.dataframe(df)
                        else:
                            st.info("Esegui il Generatore Test per visualizzare i risultati")

        with tab4:
            st.subheader("Analisi Automazione")
            for i, (req, res) in enumerate(zip(st.session_state.multi_requirements, st.session_state.multi_results["AnalizzatoreAutomazione"])):
                if req.strip():
                    with st.expander(f"Automazione Requisito {i+1}: {req[:50]}..."):
                        # Copia e incolla la logica di visualizzazione della tabella dalla single_requirement_page per AnalizzatoreAutomazione
                        # Adatta le key degli elementi di sessione
                        # Visualizzazione dei risultati
                        if res:
                            # Dividi il risultato in linee
                            lines = res.strip().split('\n')

                            # Estrai l'header (prima linea)
                            headers = [h.strip() for h in lines[1].split('|')]

                            # Estrai i dati (tutte le linee successive) e filtra le righe
                            data = []
                            for line in lines[3:]:  # Salta la prima linea (header) e la seconda (separatore)
                                if line.strip():  # Ignora linee vuote
                                    row = [d.strip().replace(';', ';\n') for d in line.split('|')]
                                    # Verifica se ci sono celle vuote o con "None" nella riga
                                    if not any(not cell or cell.lower() == '```' for cell in row):
                                        data.append(row)

                            # Crea un DataFrame pandas per visualizzazione
                            df = pd.DataFrame(data, columns=headers)

                            # Visualizza la tabella con gli header corretti
                            st.dataframe(df)

                        else:
                            st.info("Esegui l'Analizzatore Automazione per visualizzare i risultati")

        with tab5:
            st.subheader("Analisi Performance")
            for i, (req, res) in enumerate(zip(st.session_state.multi_requirements, st.session_state.multi_results["AnalistaPerformance"])):
                if req.strip():
                    with st.expander(f"Performance Requisito {i+1}: {req[:50]}..."):
                        # Copia e incolla la logica di visualizzazione della tabella dalla single_requirement_page per AnalistaPerformance
                        # Adatta le key degli elementi di sessione
                        if res:
                            try:
                                # Pulizia e preparazione dei dati
                                lines = [line.strip() for line in res.split('\n') if line.strip()]

                                # Estrazione delle colonne (prima riga valida dopo eventuali header)
                                header = None
                                data_lines = []

                                for line in lines:
                                    if line.startswith("Necessari?|"):
                                        header = [h.strip() for h in line.split('|')]
                                    elif line.startswith("---|"):
                                        continue
                                    elif header and '|' in line:
                                        data_lines.append([cell.strip() for cell in line.split('|')])

                                if header and data_lines:
                                    # Verifica che tutte le righe abbiano lo stesso numero di colonne dell'header
                                    valid_data = []
                                    for row in data_lines:
                                        if len(row) == len(header):
                                            valid_data.append(row)

                                    if valid_data:
                                        df = pd.DataFrame(valid_data, columns=header)
                                        st.dataframe(df)
                                    else:
                                        st.error("Formattazione dati non valida. Nessuna riga con il numero corretto di colonne.")
                                        st.text(res)
                                else:
                                    st.error("Formato tabella non riconosciuto nell'output.")
                                    st.text(res)

                            except Exception as e:
                                st.error(f"Errore durante l'elaborazione dei risultati: {str(e)}")
                                st.text(res)
                        else:
                            st.info("Esegui l'analisi per valutare i performance test necessari")


def main():
    st.markdown(
        """
        <style>
            div[role="radiogroup"] > label {
                display: inline-flex;
                align-items: center;
                margin-right: 10px;
            }
            .block-container {
                padding-top: 0 !important;
            }
            .stAppHeader {
                display: none}
        </style>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Seleziona modalità:",
        ["Requisito", "Multi-Requisiti", "Jira Story"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.title("🤖 (TEST)INA")

    if page == "Requisito":
        single_requirement_page()
    elif page == "Multi-Requisiti":
        multiple_requirements_page()
    elif page == "Jira Story":
        jira_integration_page()


if __name__ == "__main__":
    main()
