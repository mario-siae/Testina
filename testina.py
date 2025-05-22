import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
import requests
from atlassian import Jira
import time
import re # Importato per le espressioni regolari

# Carica le variabili d'ambiente
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  
JIRA_URL = os.getenv("JIRA_URL")  
JIRA_USERNAME = os.getenv("JIRA_USERNAME")  
JIRA_TOKEN = os.getenv("JIRA_TOKEN")  

global_model_selection = ""

wait_time = 60
max_retries = 3

# Configurazione iniziale
st.set_page_config(
    page_title="(TEST)INA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# Database di conoscenza
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
                "utenti_accessibili": ["Artisti", "Organizzatore Professionale", "Delegati"],
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

CSS_VALUTATORE_STYLE = """
<style>
    /* Stili per i box degli elementi in base al tema */
    @media (prefers-color-scheme: dark) {
        .dark-mode-present { background-color: #006400 !important; color: #ffffff !important; border-left: 4px solid #00FF00;}
        .dark-mode-missing { background-color: #8B0000 !important; color: #ffffff !important; border-left: 4px solid #FF4500;}
        .dark-mode-improved { background-color: #00008B !important; color: #ffffff !important; border-left: 4px solid #1E90FF;}
        .dark-mode-notes { background-color: #8B8000 !important; color: #ffffff !important; border-left: 4px solid #FFD700;}
    }
    @media (prefers-color-scheme: light) {
        .dark-mode-present { background-color: #90EE90 !important; color: #006400 !important; border-left: 4px solid #008000;}
        .dark-mode-missing { background-color: #FFA07A !important; color: #8B0000 !important; border-left: 4px solid #FF0000;}
        .dark-mode-improved { background-color: #ADD8E6 !important; color: #000080 !important; border-left: 4px solid #0000FF;}
        .dark-mode-notes { background-color: #FFFACD !important; color: #8B8000 !important; border-left: 4px solid #FFD700;}
    }
    .element-box {
        padding: 12px 15px !important;
        border-radius: 6px !important;
        margin: 8px 0 !important;
        font-weight: 500 !important;
    }
    .improved-box {
        padding: 18px 20px !important;
        margin-bottom: 25px !important;
        font-size: 1.05em !important;
    }
</style>
"""

# Autenticazione con password semplice
def check_password():
    def password_entered():
        if st.session_state["password"] == os.getenv("DASHBOARD_PASSWORD"):
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 Accesso alla Dashboard")
        st.text_input("Inserisci la password", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ Password errata")
        st.stop()


check_password()  # 👈 Blocca l'accesso se la password è errata

@st.cache_resource # Cache Jira instance
def get_jira_instance():
    try:
        session = requests.Session()

        jira = Jira(
            url=JIRA_URL,
            username=JIRA_USERNAME,
            password=JIRA_TOKEN, # Use st.secrets for this
            session=session
        )
        # Test connection
        jira.myself()
        return jira
    except Exception as e:
        st.error(f"Errore di connessione a Jira: {e}. Verifica URL, credenziali, token e connessione VPN/proxy.")
        return None

@st.cache_resource
def get_genai_client():
    try:
        # Ensure GEMINI_API_KEY is loaded correctly, e.g., from st.secrets or .env
        api_key_to_use = GEMINI_API_KEY
        if not api_key_to_use or "YOUR_API_KEY" in api_key_to_use:
            st.error("GEMINI_API_KEY non configurato correttamente. "
                     "Impostala nelle variabili d'ambiente o nei secrets di Streamlit.")
            return None

        # This is the standard way to configure the google-generativeai library
        genai.configure(api_key=api_key_to_use)
        
        # Test with a lightweight call if necessary, e.g., listing models,
        # but configure() itself should work if the module is correct.
        # For now, we assume configure() is the point of failure as per the error.
        
        return genai # Return the configured genai module
        
    except AttributeError as e:
        if "'module' object has no attribute 'configure'" in str(e) or \
           "'google.genai' has no attribute 'configure'" in str(e): # More specific check
            st.error(f"Errore di attributo con GenAI (genai.configure): {e}. "
                     "Questo solitamente indica che:\n"
                     "1. La libreria 'google-generativeai' non è installata correttamente o è una versione obsoleta.\n"
                     "2. C'è un conflitto di nomi: un file 'google.py' o 'genai.py' nella tua directory di progetto.\n"
                     "3. Stai tentando di usare una libreria diversa da 'google-generativeai' che ha un'API differente.\n"
                     "Assicurati di avere installato 'pip install google-generativeai' e che non ci siano conflitti.")
        else:
            st.error(f"Errore di attributo sconosciuto con GenAI: {e}")
        return None
    except Exception as e:
        st.error(f"Errore generico durante la configurazione del client GenAI: {e}")
        return None


@st.cache_data # Cache Jira projects for a short time
def get_jira_projects(_jira): # Pass Jira instance with underscore to use Streamlit's caching correctly
    if _jira:
        try:
            projects = _jira.projects()
            # Handle both list of dicts and list of Project objects
            if projects and isinstance(projects[0], dict):
                return {project['key']: project['name'] for project in projects}
            else:
                return {project.key: project.name for project in projects}
        except Exception as e:
            st.error(f"Errore nel recupero dei progetti Jira: {e}")
    return {}

@st.cache_data(ttl=300) # Cache issues for 5 minutes
def get_project_issues(_jira, project_key, issue_types_tuple): # issue_types must be hashable (tuple)
    if _jira and project_key:
        # Make issue_types_tuple a string for JQL
        issue_types_str = ','.join([f'"{it}"' for it in issue_types_tuple])
        jql_query = f"project={project_key} AND issuetype in ({issue_types_str}) ORDER BY created DESC"
        try:
            issues = _jira.jql(jql_query, limit=100) # Added limit
            return issues['issues'] if issues else []
        except Exception as e:
            st.error(f"Errore nel recupero delle issue: {e}")
    return []

def parse_structured_text_to_sections(text_input: str):
    if not text_input:
        return {key_info["key"]: "Nessun contenuto disponibile."
                for key_info in [
                    {"key": "contesto"}, {"key": "attori"}, {"key": "scenari"},
                    {"key": "variabili"}, {"key": "flusso"}
                ]}
    section_details = [
        {"key": "contesto", "pattern_str": r"1\.\s*\*\*\s*Contesto Generale\s*\*\*"},
        {"key": "attori", "pattern_str": r"2\.\s*\*\*\s*Attori Coinvolti\s*\*\*"},
        {"key": "scenari", "pattern_str": r"3\.\s*\*\*\s*Scenari\s*\*\*:?"},
        {"key": "variabili", "pattern_str": r"4\.\s*\*\*\s*Variabili Dinamiche\s*\*\*"},
        {"key": "flusso", "pattern_str": r"###\s*Flusso di Lavoro\s*:?"},
    ]
    for detail in section_details:
        detail["regex"] = re.compile(detail["pattern_str"], re.IGNORECASE | re.DOTALL)

    found_headers = []
    for detail in section_details:
        for match in detail["regex"].finditer(text_input):
            found_headers.append({
                "key": detail["key"],
                "start_header": match.start(),
                "end_header": match.end()
            })
    found_headers.sort(key=lambda x: x["start_header"])
    parsed_content = {detail["key"]: "" for detail in section_details}
    num_found = len(found_headers)
    for i, header_match in enumerate(found_headers):
        current_key = header_match["key"]
        content_start_index = header_match["end_header"]
        content_end_index = len(text_input)
        if i + 1 < num_found:
            content_end_index = found_headers[i+1]["start_header"]
        content = text_input[content_start_index:content_end_index].strip()
        parsed_content[current_key] = content
    for detail in section_details:
        key = detail["key"]
        if not parsed_content.get(key, "").strip():
            parsed_content[key] = "Nessun contenuto trovato per questa sezione."
    return parsed_content

def _parse_markdown_table_to_df(md_table_string):
    if not md_table_string or not isinstance(md_table_string, str):
        return pd.DataFrame()
    lines = [line.strip() for line in md_table_string.strip().split('\n') if line.strip() and '|' in line]
    if not lines: return pd.DataFrame()

    header_line_index = -1
    for i, line in enumerate(lines):
        if not line.startswith('---') and not all(c in '-| ' for c in line):
             # Potential header if it's the first line with '|' or follows a non-data line.
            if header_line_index == -1: # Take the first valid candidate as header
                header_line_index = i
                break # Assume first valid line is header for simplicity of this parser

    if header_line_index == -1 : return pd.DataFrame() # No header found

    header = [h.strip() for h in lines[header_line_index].split('|') if h.strip()]
    
    data_lines = []
    separator_found_after_header = False
    for i in range(header_line_index + 1, len(lines)):
        line = lines[i]
        if line.startswith('---') or all(c in '-| ' for c in line):
            separator_found_after_header = True
            continue
        if separator_found_after_header and header: # Only parse data after separator
            cells = [cell.strip() for cell in line.split('|')]
            # Adjust row length to header length
            if len(cells) > len(header): cells = cells[:len(header)]
            while len(cells) < len(header): cells.append("")
            data_lines.append(cells)
        elif not separator_found_after_header and header and i == header_line_index + 1 and not (line.startswith('---') or all(c in '-| ' for c in line)):
            # If no separator line immediately after header, assume this is data
            cells = [cell.strip() for cell in line.split('|')]
            if len(cells) > len(header): cells = cells[:len(header)]
            while len(cells) < len(header): cells.append("")
            data_lines.append(cells)


    if header and data_lines:
        try:
            df = pd.DataFrame(data_lines, columns=header)
            return df
        except Exception as e:
            # Fallback if column numbers mismatch
            # print(f"Error creating DataFrame: {e}. Header: {header}, First data row: {data_lines[0] if data_lines else 'No data'}")
            # Attempt to create with generic column names if mismatch
            if data_lines:
                max_cols = max(len(row) for row in data_lines)
                # If header is shorter than max_cols in data, it's problematic.
                # For simplicity, we'll truncate data or pad header if possible,
                # but a robust parser would handle this more gracefully.
                # This simplified parser assumes header is mostly correct or data will be truncated.
                if len(header) < max_cols and len(header) > 0: # If header is too short, use its length
                    data_lines_adjusted = [row[:len(header)] for row in data_lines]
                    return pd.DataFrame(data_lines_adjusted, columns=header)
                elif len(header) >= max_cols and max_cols > 0: # If header is adequate or longer
                     return pd.DataFrame(data_lines, columns=header[:max_cols if max_cols > 0 else 1])


    # Fallback for tables without a '---' separator line but with a clear header
    if header and data_lines and not separator_found_after_header and len(lines) > header_line_index +1 :
         # This case is now partially handled above
         pass

    # print(f"Could not parse table. Header found: {header}. Data lines found: {len(data_lines)}") # Debug
    return pd.DataFrame()


# --- Agent Core Functions 
def run_valutatore_requisiti(requisito, client_gemini, model=global_model_selection): # Updated model
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
    model_instance = client_gemini.GenerativeModel(model_name=model)
    response = model_instance.generate_content(prompt)
    return response.text

def run_analista_requisiti(requisito, client_gemini, model=global_model_selection, previous_analysis_feedback=None): # Updated model
    context = ""
    for system_id, system_info in KNOWLEDGE_BASE.items():
        if system_id.lower() in requisito.lower():
            context = f"Informazioni dal knowledge base per il sistema {system_id}:\n"
            context += "\n".join([f"{key}: {value}" for key, value in system_info.items()])
            break

    system_instruction = "Sei un assistente specializzato nell'analisi dei requisiti software. Rispondi in formato testo strutturato."
    feedback_prompt_section = ""
    if previous_analysis_feedback:
        feedback_prompt_section = f"""
        Una precedente valutazione del requisito ha fornito i seguenti suggerimenti, una versione migliorata o un'analisi. Prendine atto per la tua analisi attuale:
        ---
        {previous_analysis_feedback}
        ---
        Considera attentamente quanto sopra nel formulare la tua risposta. Se è stata fornita una versione migliorata del requisito, basa la tua analisi principalmente su quella, integrandola con il requisito originale se necessario.
        """

    prompt = f"""
    {system_instruction}
    {feedback_prompt_section}

    Analizza il seguente requisito software (considera il requisito originale e l'eventuale feedback fornito sopra). Fornisci:
    1. Il contesto generale del requisito (di cosa si tratta, qual è l'obiettivo)
    2. I principali attori/utenti coinvolti
    3. Gli scenari d'uso:
       - Scenari principali (flusso normale)
       - Scenari alternativi (flussi alternativi plausibili)
       - Scenari negativi (situazioni in cui qualcosa non funziona)
       - Corner cases (situazioni limite)
    4. Le variabili dinamiche presenti nel requisito
    5. Flusso di lavoro strutturato

    Ecco il requisito principale da analizzare (integra con il feedback se presente):
    {requisito}

    {context}

    Fornisci la tua valutazione in questo formato ESATTO (non aggiungere altro testo prima o dopo):

    1. **Contesto Generale**
    - [Il contesto generale del requisito (di cosa si tratta, qual è l'obiettivo)]

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

    . **Rispondi solo in italiano, fornisci SOLO la struttura richiesta, senza testo pre e post.**
    """
    model_instance = client_gemini.GenerativeModel(model_name=model)
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < max_retries - 1: time.sleep(wait_time)
            else: raise

def run_analista_rischio(requisiti_analysis, client_gemini, model=global_model_selection): # Updated model
    prompt = f"""
        **Ruolo:** Sei un Analista di Rischio esperto, incaricato di valutare i rischi associati ai casi d'uso identificati nell'analisi dei requisiti fornita.
        **Obiettivo:** Generare un'analisi dei rischi in formato tabellare, facilmente convertibile in una tabella Markdown.
        **Formato Tabellare Richiesto (DEVI USARE QUESTO ESATTO FORMATO PER L'HEADER DELLA TABELLA):**
        ```
        ID|Scenario|Criticità|Fattore di Rischio|Motivazione|Frequenza|Rischio Finale
        ---|---|---|---|---|---|---
        ```
        **Per ogni scenario presente nell'analisi dei requisiti (sezione "3. **Scenari**"), devi fornire le seguenti informazioni:**
        * **ID:** Un identificatore univoco per il rischio (es. RS001, RS002, ecc.). Assicurati che ogni riga abbia un ID unico.
        * **Scenario:** Una breve descrizione del caso d'uso o della funzionalità a cui si riferisce il rischio. Copia o riassumi lo scenario dall'analisi dei requisiti. Se non ci sono scenari espliciti, indica che non è possibile generare l'analisi.
        * **Criticità:** Una descrizione concisa della potenziale conseguenza negativa o del problema che potrebbe verificarsi.
        * **Fattore di Rischio:** Una valutazione qualitativa della probabilità che l'evento critico si verifichi (Basso, Medio, Alto).
        * **Motivazione:** Una breve spiegazione del perché hai assegnato quel particolare fattore di rischio. Considera fattori come la complessità, le dipendenze, la familiarità del team, ecc.
        * **Frequenza:** La frequenza prevista con cui lo scenario o la funzionalità verranno utilizzati (Rara, Occasionale, Frequente).
        * **Rischio Finale:** Una valutazione del rischio complessivo, derivata dalla combinazione della Criticità, del Fattore di Rischio e della Frequenza. Puoi usare una logica semplice (es. Basso + Rara = Basso, Alto + Frequente = Alto) o una tua expertise.

        **Importante:**
        * **Rispondi unicamente con la tabella formattata in Markdown**, utilizzando il carattere `|` come separatore di colonne, come mostrato nell'esempio sopra. Non includere alcun altro testo o spiegazione al di fuori della tabella.
        * Assicurati che la tabella sia ben formattata e facilmente parsabile. L'HEADER DEVE ESSERE ESATTAMENTE `ID|Scenario|Criticità|Fattore di Rischio|Motivazione|Frequenza|Rischio Finale` seguito dalla linea `---|---|---|---|---|---|---`.
        * Analizza attentamente ogni scenario presente nell'analisi dei requisiti fornita. Se l'input `requisiti_analysis` è vuoto o non contiene scenari validi, restituisci una tabella vuota o un messaggio che indica "Nessuno scenario fornito per l'analisi dei rischi." dentro la tabella.

        **Analisi dei Requisiti:**
        ```
        {requisiti_analysis}
        ```
        """
    model_instance = client_gemini.GenerativeModel(model_name=model)
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < max_retries - 1: time.sleep(wait_time)
            else: raise

def run_generatore_test(requisiti_analysis, rischio_analysis, client_gemini, model=global_model_selection): # Updated model
    prompt = f"""
        Sei un Test Engineer esperto. Il tuo compito è generare test case completi basati sull'analisi dei requisiti e sull'analisi del rischio.
        Devi generare i test case in un formato strutturato che possa essere facilmente convertito in una tabella, seguendo ESATTAMENTE questo schema per ogni test case, inclusa la riga di separazione dell'header:
        ID|Titolo|Precondizioni|Passi|Risultato Atteso|Scenario|Rischio
        ---|------|------------|-----|---------------|--------|------
        Per ogni test case, specifica:
        - ID univoco del test (es. TC001)
        - Titolo descrittivo
        - Precondizioni (se non ci sono, scrivi "Nessuna")
        - Passi da eseguire (separati da '; ' se multipli, o numerati con 1. 2. 3.)
        - Risultato atteso
        - Scenario coperto (derivato dall'analisi dei requisiti)
        - Livello di rischio associato (Basso, Medio, Alto - derivato dall'analisi del rischio)

        Verifica poi che tutti gli scenari principali, alternativi, negativi e corner case identificati nell'analisi dei requisiti siano coperti da almeno un caso di test.
        Dai priorità ai test case che coprono scenari ad alto rischio.

        Ecco l'analisi dei requisiti:
        ```
        {requisiti_analysis}
        ```

        Ecco l'analisi del rischio:
        ```
        {rischio_analysis}
        ```
        **Rispondi solo con la tabella Markdown formattata come sopra, niente altro testo prima o dopo.**
        Se non è possibile generare test case (es. input insufficienti), restituisci una tabella vuota con solo l'header e la riga di separazione.
        """
    model_instance = client_gemini.GenerativeModel(model_name=model)
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < max_retries - 1: time.sleep(wait_time)
            else: raise

def run_analizzatore_automazione(test_cases, client_gemini, model=global_model_selection): # Updated model
    prompt = f"""
        Agisci come un Automation Engineer esperto con una forte mentalità orientata al ROI (Return on Investment). Il tuo compito è analizzare una serie di test case e determinare la loro idoneità all'automazione, considerando attentamente il bilanciamento tra il valore dell'automazione e l'effort necessario per implementarla in termini di tempo e risorse (costo). Suggerisci lo strumento più appropriato (Postman per test API o modifiche dati, Cypress per test end-to-end web, Appium per test end-to-end mobile) e assegna una priorità di automazione, concentrandoti sull'automazione di test **critici e fondamentali per la stabilità e la funzionalità in ambiente di produzione**.
        Identifica come casi da automatizzare solo quelli che in rapporto costi/benefici rappresentano un importante valore aggiunto tale da giustificare la spesa.
        Dopo aver identificato i casi, restringili a quelli che si possono ripetere in produzione senza richiedere azioni dispositive (es storni a seguito di pagamenti per fare un test ecc).

        Fornisci la tua analisi in un formato tabellare Markdown, seguendo rigorosamente questa struttura (USA QUESTO ESATTO HEADER):

        ID Test|Titolo Test|Adatto Automazione?|Strumento Consigliato|Priorità Automazione|Stima Effort (Giorni Uomo)|Note Implementazione
        ---|---|---|---|---|---|---

        Per ogni test case fornito, valuta attentamente i seguenti aspetti:
        - ID Test: Riporta l'ID univoco del test case.
        - Titolo Test: Fornisci una breve e chiara descrizione del test.
        - Adatto Automazione?: Indica con "Sì" o "No" se il test è un buon candidato per l'automazione **considerando il rapporto tra il valore dell'automazione (riduzione del rischio in produzione, frequenza di esecuzione, tempo risparmiato a lungo termine) e l'effort stimato per implementarla**. Automatizza solo i test che portano un beneficio significativo in ottica di produzione.
        - Strumento Consigliato: Se "Adatto Automazione?" è "Sì", specifica lo strumento di automazione suggerito tra "Postman", "Cypress", "Appium". Se il test non è adatto, indica "Nessuno".
        - Priorità Automazione: Assegna una priorità all'automazione ("Alta", "Media", "Bassa") basata sull'**importanza del test per la stabilità in produzione, la frequenza di esecuzione e il ROI potenziale**. Concentrati sull'automatizzare con alta priorità i test fondamentali e critici.
        - Stima Effort (Giorni Uomo): Fornisci una stima approssimativa dell'effort necessario per automatizzare completamente il test in termini di giorni uomo (es. 0.5, 1, 2). Considera la complessità del test, la familiarità con lo strumento e la necessità di eventuali setup specifici.
        - Note Implementazione: Includi eventuali considerazioni specifiche sull'implementazione dell'automazione per questo test, come prerequisiti, sfide potenziali, strategie particolari o se ci sono alternative all'automazione che potrebbero essere più efficienti. Se non ci sono note particolari, scrivi "Nessuna".

        **Rispondi unicamente con la tabella Markdown formattata**, senza aggiungere alcun altro testo o spiegazione. Assicurati che la tabella sia ben formattata con il carattere '|' come separatore di colonne e l'header specificato.
        Se l'input `test_cases` è vuoto o non valido, restituisci una tabella vuota con solo l'header e la riga di separazione.

        Ecco i test case da analizzare:
        ```
        {test_cases}
        ```
    """
    model_instance = client_gemini.GenerativeModel(model_name=model)
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            # Simplified error handling for brevity in refactoring, original was more specific
            if attempt < max_retries - 1: time.sleep(wait_time)
            else: raise

def run_analista_performance(requisiti_analysis, rischio_analysis, client_gemini, model=global_model_selection): # Updated model
    prompt = f"""
    Sei un Performance Test Engineer esperto. Analizza i requisiti e i rischi per determinare se sono necessari performance test.
    Rispondi in formato tabellare strutturato (usando | come separatore), seguendo ESATTAMENTE questo schema (USA QUESTO ESATTO HEADER):

    Necessari?|Tipo Test|Metriche Chiave|Soglie Ideali|Utenti Simulati|Note
    ---|---|---|---|---|---
    [Sì/No]|[Load/Stress/Endurance/Spike/Scalability]|[es. Latenza (ms), Throughput (RPS), Error Rate (%)]|[es. Latenza <200ms, Error Rate <0.1%]|[es. 100-1000 concurrent users]|[Considerazioni aggiuntive, scenari critici da testare]

    IMPORTANTE:
    1. Usa SOLO il formato sopra specificato.
    2. Non aggiungere testo prima o dopo la tabella.
    3. Assicurati che ogni riga abbia ESATTAMENTE 6 colonne separate da |.
    4. Se non sono necessari test di performance, la prima colonna "Necessari?" deve essere "No" e le altre possono contenere "N/A" o brevi spiegazioni.

    Criteri per raccomandare performance test:
    - Presenza di scenari ad alto traffico identificati nell'analisi dei requisiti (es. pagamenti, login massivi, ricerche frequenti).
    - Requisiti non funzionali espliciti relativi a performance (es. "il sistema deve supportare 1000 richieste per secondo").
    - Rischio alto di colli di bottiglia identificato nell'analisi dei rischi (es. dovuto a dipendenze da database, API esterne lente, algoritmi complessi).
    - Componenti critici per il business il cui fallimento sotto carico avrebbe impatti significativi (es. checkout, flussi di pagamento, core functionalities).
    - Introduzione di nuove tecnologie o cambiamenti architetturali significativi.

    Se l'analisi dei requisiti o dei rischi non fornisce informazioni sufficienti per una valutazione, indicalo nelle Note.

    Ecco l'analisi dei requisiti:
    ```
    {requisiti_analysis}
    ```

    Ecco l'analisi del rischio:
    ```
    {rischio_analysis}
    ```
    """
    model_instance = client_gemini.GenerativeModel(model_name=model)
    response = model_instance.generate_content(prompt)
    return response.text

def run_analista_gestionale(test_cases, client_gemini, model=global_model_selection): # Updated model
    prompt = f"""
    Sei un Analista Gestionale esperto in QA IT con 10+ anni di esperienza nella stima degli effort di testing manuale.
    Il tuo compito è stimare l'effort necessario per eseguire manualmente i test case forniti, considerando una call Teams tra tester e business per la review e l'esecuzione.

    Linee guida per la stima (per ogni test case):
    1. **Analisi Test Case e Setup Iniziale**: 10 minuti base per test case (comprensione, preparazione dati/ambiente se minimi).
    2. **Esecuzione Passi**:
        - Step Semplice (es. click, input testo semplice, verifica UI elementare): 2-3 minuti per step.
        - Step Medio (es. compilazione form con più campi, navigazione tra poche pagine, verifica dati semplice): 4-6 minuti per step.
        - Step Complesso (es. esecuzione di un flusso end-to-end breve, validazioni multiple, verifiche su DB/API di base, setup dati specifico): 7-10 minuti per step.
    3. **Verifica Risultati e Documentazione**: 5-10 minuti per test case (confronto risultati attesi, cattura screenshot per fallimenti, log).
    4. **Contingency Buffer**: Aggiungi un 15-20% sul totale stimato per imprevisti, discussioni, chiarimenti durante la sessione.
    5. **Man Days**: Considera 1 Man Day = 7 ore effettive di lavoro. Arrotonda i Man Days al mezzo giorno più vicino (es. 0.5, 1, 1.5 MD).

    Formato richiesto per l'output (DEVI USARE ESATTAMENTE QUESTO FORMATO):

    ### Stima Effort Test Manuali

    **Riepilogo Generale**
    - Totale Test Case Analizzati: [Numero Totale dei Test Case Forniti]
    - Stima Ore Totali Esecuzione (inclusa analisi, setup, verifica, contingency): [Y] ore
    - Stima Man Days Complessivi Necessari: [L] MD

    **Dettaglio per Test Case**
    (Ripeti questa sezione per ogni Test Case fornito. Se non ci sono test case, indica "Nessun test case fornito per la stima.")

    **Test Case [ID Test Case]: [Titolo Test Case]**
    - Numero di Passi Stimati: [Numero di passi logici identificati nel test case]
    - Complessità Media Stimata Passi: [Semplice/Media/Complessa/Mista]
    - Stima Tempo Esecuzione Singolo Test Case (minuti): [Totale minuti per questo TC, inclusi analisi, setup, esecuzione, verifica]
    - Note sulla stima: [Eventuali considerazioni specifiche per la stima di questo TC, es. "Richiede setup dati complesso", "Verifica su sistema esterno"]
    ---

    Analizza questi test case:
    ```
    {test_cases}
    ```

    **Rispondi solo in italiano con il formato richiesto. Non aggiungere testo introduttivo o conclusivo al di fuori della struttura specificata.**
    Se l'input `test_cases` è vuoto, indica nel riepilogo "Nessun test case fornito" e ometti la sezione di dettaglio.
    """
    model_instance = client_gemini.GenerativeModel(model_name=model)
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < max_retries - 1: time.sleep(wait_time)
            else: raise


# --- Central Agent Definitions & Pipeline Orchestration ---
AGENT_SPECS = {
    "ValutatoreRequisiti": {
        "run_function": run_valutatore_requisiti,
        "button_label": "Valutatore Requisiti",
        "inputs": {"requisito": "original_requirement"},
    },
    "AnalistaRequisiti": {
        "run_function": run_analista_requisiti,
        "button_label": "Analista Requisiti",
        "inputs": {"requisito": "original_requirement", "previous_analysis_feedback": "ValutatoreRequisiti"},
    },
    "AnalistaRischio": {
        "run_function": run_analista_rischio,
        "button_label": "Analista Rischio",
        "inputs": {"requisiti_analysis": "AnalistaRequisiti"},
    },
    "GeneratoreTest": {
        "run_function": run_generatore_test,
        "button_label": "Generatore Test",
        "inputs": {"requisiti_analysis": "AnalistaRequisiti", "rischio_analysis": "AnalistaRischio"},
    },
    "AnalizzatoreAutomazione": {
        "run_function": run_analizzatore_automazione,
        "button_label": "Analizzatore Automazione",
        "inputs": {"test_cases": "GeneratoreTest"},
    },
    "AnalizzatorePerformance": {
        "run_function": run_analista_performance,
        "button_label": "Analizzatore Performance",
        "inputs": {"requisiti_analysis": "AnalistaRequisiti", "rischio_analysis": "AnalistaRischio"},
    },
    "AnalistaGestionale": {
        "run_function": run_analista_gestionale,
        "button_label": "Analista Gestionale",
        "inputs": {"test_cases": "GeneratoreTest"},
    }
}
AGENT_PIPELINE_ORDER = [
    "ValutatoreRequisiti", "AnalistaRequisiti", "AnalistaRischio",
    "GeneratoreTest", "AnalizzatoreAutomazione", "AnalizzatorePerformance",
    "AnalistaGestionale"
]

def execute_agent_logic(req_id, agent_id, original_requirement_text, client_gemini, model_selection):
    if req_id not in st.session_state.analysis_results:
        st.session_state.analysis_results[req_id] = {}

    agent_spec = AGENT_SPECS[agent_id]
    kwargs = {}
    all_inputs_available = True

    for kwarg_name, source_key in agent_spec["inputs"].items():
        if source_key == "original_requirement":
            kwargs[kwarg_name] = original_requirement_text
        else:
            source_agent_data = st.session_state.analysis_results.get(req_id, {}).get(source_key, {})
            if source_agent_data.get("status") == "completed":
                kwargs[kwarg_name] = source_agent_data["output"]
            else:
                all_inputs_available = False
                st.session_state.analysis_results[req_id][agent_id] = {
                    "status": "blocked",
                    "output": f"Input '{source_key}' non disponibile (stato: {source_agent_data.get('status', 'non eseguito')})."
                }
                return  # ⚠️ NON usare st.rerun() qui

    if not all_inputs_available:
        return  # ⚠️ Nessun st.rerun() qui

    try:
        st.session_state.analysis_results[req_id][agent_id] = {"status": "running", "output": None}
        result = agent_spec["run_function"](client_gemini=client_gemini, model=model_selection, **kwargs)
        st.session_state.analysis_results[req_id][agent_id] = {"status": "completed", "output": result}
    except Exception as e:
        st.session_state.analysis_results[req_id][agent_id] = {"status": "error", "output": str(e)}

def run_full_analysis_pipeline(req_id, original_requirement_text, client_gemini, model_selection):
    if not original_requirement_text or not original_requirement_text.strip():
        st.warning(f"Requisito per '{req_id}' è vuoto. Analisi saltata.")
        st.session_state.analysis_results[req_id] = {
            agent_id: {"status": "skipped", "output": "Requisito vuoto"} for agent_id in AGENT_PIPELINE_ORDER
        }
        st.rerun() # MANTIENI: corretto per saltare questo item e rieseguire lo script
        return

    if req_id not in st.session_state.analysis_results:
         st.session_state.analysis_results[req_id] = {}

    for agent_id_init in AGENT_PIPELINE_ORDER:
        if agent_id_init not in st.session_state.analysis_results.get(req_id, {}) or \
           st.session_state.analysis_results[req_id][agent_id_init].get("status") not in ["completed", "running"]:
            st.session_state.analysis_results[req_id][agent_id_init] = {"status": "pending", "output": None}

    for agent_id in AGENT_PIPELINE_ORDER:
        current_status_data = st.session_state.analysis_results.get(req_id, {}).get(agent_id, {})
        current_status = current_status_data.get("status")

        if current_status == "completed":
            continue
        if current_status == "running": 
            continue

        execute_agent_logic(req_id, agent_id, original_requirement_text, client_gemini, model_selection)

        updated_status_data = st.session_state.analysis_results.get(req_id, {}).get(agent_id, {})
        if updated_status_data.get("status") in ["error", "blocked"]:
            current_agent_index = AGENT_PIPELINE_ORDER.index(agent_id)
            for subsequent_agent_id in AGENT_PIPELINE_ORDER[current_agent_index+1:]:
                if subsequent_agent_id not in st.session_state.analysis_results.get(req_id,{}) or \
                    st.session_state.analysis_results[req_id].get(subsequent_agent_id,{}).get("status") == "pending":
                    st.session_state.analysis_results[req_id][subsequent_agent_id] = {
                        "status": "skipped_dependency",
                        "output": f"Pipeline interrotta a {agent_id} ({updated_status_data.get('status')})"
                    }
            st.rerun() # MANTIENI: corretto per interrompere la pipeline per questo req_id e aggiornare l'UI
            return 


# --- Unified Display Logic ---
def _extract_valutatore_section(content, section_title):
    if not content: return ""
    # Adjusted pattern to be more robust for section titles ending with ':'
    pattern = re.compile(r"###\s*" + re.escape(section_title) + r":?\s*\n(.*?)(?=\n###\s|\Z)", re.S)
    match = pattern.search(content)
    return match.group(1).strip() if match else ""

def display_valutatore_output_unified(result_text):
    st.markdown(CSS_VALUTATORE_STYLE, unsafe_allow_html=True) # Ensure CSS is applied here
    completezza = _extract_valutatore_section(result_text, "Valutazione Completezza")
    presenti_text = _extract_valutatore_section(result_text, "Elementi Presenti")
    mancanti_text = _extract_valutatore_section(result_text, "Elementi Mancanti")
    migliorato = _extract_valutatore_section(result_text, "Requisito Migliorato")
    note = _extract_valutatore_section(result_text, "Note")

    st.markdown("#### 📊 Valutazione Completezza")
    if completezza:
        if "requisito completo" in completezza.lower() and not "parzialmente" in completezza.lower() and not "non completo" in completezza.lower() and not "incompleto" in completezza.lower() : st.success(f"✅ {completezza}")
        elif "parzialmente completo" in completezza.lower(): st.warning(f"⚠️ {completezza}")
        elif "incompleto" in completezza.lower() or "non completo" in completezza.lower(): st.error(f"❌ {completezza}")
        else: st.info(completezza) # Default display if keywords not matched
    else: st.info("Nessuna valutazione di completezza disponibile.")

    st.markdown("#### 🔍 Elementi Identificati")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### ✅ Presenti")
        if presenti_text:
            present_items = [item.strip()[2:] for item in presenti_text.split('\n') if item.strip().startswith("- ")]
            if present_items:
                for item_val in present_items: st.markdown(f"<div class='element-box dark-mode-present'><strong>✓ {item_val}</strong></div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='element-box dark-mode-present'><strong>{presenti_text}</strong></div>", unsafe_allow_html=True) # Show raw if not list
        else: st.info("Nessuna informazione sugli elementi presenti.")
    with col2:
        st.markdown("##### ❌ Mancanti")
        if mancanti_text:
            missing_items = [item.strip()[2:] for item in mancanti_text.split('\n') if item.strip().startswith("- ")]
            if missing_items:
                for item_val in missing_items: st.markdown(f"<div class='element-box dark-mode-missing'><strong>✗ {item_val}</strong></div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='element-box dark-mode-missing'><strong>{mancanti_text}</strong></div>", unsafe_allow_html=True) # Show raw if not list
        else: st.info("Nessuna informazione sugli elementi mancanti.")

    if migliorato:
        st.markdown("#### ✨ Requisito Migliorato")
        st.markdown(f"<div class='element-box improved-box dark-mode-improved'>{migliorato}</div>", unsafe_allow_html=True)
    if note:
        st.markdown("#### 📝 Note Aggiuntive")
        st.markdown(f"<div class='element-box dark-mode-notes'>{note}</div>", unsafe_allow_html=True)

def display_analista_requisiti_output_unified(result_text):
    sezioni = parse_structured_text_to_sections(result_text)
    st.markdown("#### 🎯 Contesto Generale")
    st.markdown(sezioni.get("contesto", "*Nessun contenuto per Contesto Generale*"))
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 👥 Attori Coinvolti")
        st.markdown(sezioni.get("attori", "*Nessun contenuto per Attori Coinvolti*"))
    with col2:
        st.markdown("#### ⚙️ Variabili Dinamiche")
        st.markdown(sezioni.get("variabili", "*Nessun contenuto per Variabili Dinamiche*"))
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 🎬 Scenari d'Uso")
        st.markdown(sezioni.get("scenari", "*Nessun contenuto per Scenari d'Uso*"))
    with col4:
        st.markdown("#### 🛤️ Flusso di Lavoro")
        st.markdown(sezioni.get("flusso", "*Nessun contenuto per Flusso di Lavoro*"))

def display_table_output_unified(result_text, title):
    # st.subheader(title) # Subheader is now the tab title itself
    if result_text:
        df = _parse_markdown_table_to_df(result_text)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"Formato tabella per '{title}' non riconosciuto o tabella vuota.")
            st.code(result_text, language="markdown") # Show raw output if parsing fails
    else:
        st.info(f"Output per '{title}' non disponibile.")

def display_analista_gestionale_output_unified(result_text):
    # st.subheader("Analisi Gestionale QA") # Subheader is now the tab title itself
    if result_text:
        st.markdown(result_text)
    else:
        st.info("Nessun risultato disponibile per l'Analista Gestionale.")

AGENT_DISPLAY_HANDLERS = {
    "ValutatoreRequisiti": display_valutatore_output_unified,
    "AnalistaRequisiti": display_analista_requisiti_output_unified,
    "AnalistaRischio": lambda output: display_table_output_unified(output, "Analisi dei Rischi"),
    "GeneratoreTest": lambda output: display_table_output_unified(output, "Generazione Test Case"),
    "AnalizzatoreAutomazione": lambda output: display_table_output_unified(output, "Analisi Automazione"),
    "AnalizzatorePerformance": lambda output: display_table_output_unified(output, "Analisi Performance"),
    "AnalistaGestionale": display_analista_gestionale_output_unified,
}

def render_unified_analysis_tabs(req_id, original_requirement_text, client_gemini, model_selection):
    if req_id not in st.session_state.analysis_results:
        st.session_state.analysis_results[req_id] = {}
    req_results = st.session_state.analysis_results[req_id]

    tab_titles = [AGENT_SPECS[agent_id]["button_label"] for agent_id in AGENT_PIPELINE_ORDER]
    tabs = st.tabs(tab_titles)

    for i, agent_id in enumerate(AGENT_PIPELINE_ORDER):
        with tabs[i]:
            agent_spec = AGENT_SPECS[agent_id]
            # st.subheader(agent_spec["button_label"]) # Tab title serves as subheader

            agent_data = req_results.get(agent_id, {"status": "pending"})
            status = agent_data.get("status", "pending")
            output = agent_data.get("output")

            if status == "running":
                st.spinner(f"Esecuzione di {agent_id}...")
            elif status == "completed":
                display_handler = AGENT_DISPLAY_HANDLERS.get(agent_id)
                if display_handler:
                    try:
                        display_handler(output)
                    except Exception as e:
                        st.error(f"Errore nella visualizzazione del risultato di {agent_id}: {e}")
                        st.text("Dati grezzi:")
                        st.text(output)
                else:
                    st.text(output if output else "Nessun output prodotto.")
            elif status == "error":
                st.error(f"Errore in {agent_id}: {output}")
            elif status == "blocked":
                st.warning(f"{agent_id} bloccato. Causa: {output}")
            elif status == "skipped" or status == "skipped_dependency":
                st.info(f"{agent_id} saltato. Causa: {output}")
            elif status == "pending":
                 st.info(f"{agent_id} in attesa di esecuzione.")


            # Button to run individual agent
            if status not in ["running", "blocked"]: # Allow re-running if completed, error, pending, skipped
                prereqs_met = True
                missing_prereqs = []
                for _, source_key_input in agent_spec["inputs"].items():
                    if source_key_input != "original_requirement":
                        source_agent_data = req_results.get(source_key_input, {})
                        if source_agent_data.get("status") != "completed":
                            prereqs_met = False
                            missing_prereqs.append(f"{source_key_input} (stato: {source_agent_data.get('status', 'non eseguito')})")
                
                button_label_run_single = f"Esegui {agent_spec['button_label']}"
                if status == "completed": button_label_run_single = f"Riesegui {agent_spec['button_label']}"
                
                if prereqs_met:
                    if st.button(button_label_run_single, key=f"run_single_{agent_id}_{req_id}"):
                        if not original_requirement_text.strip() and "original_requirement" in agent_spec["inputs"].values() :
                            st.error("Il testo del requisito è vuoto. Impossibile eseguire l'agente.")
                        else:
                            execute_agent_logic(req_id, agent_id, original_requirement_text, client_gemini, model_selection)
                elif status != "skipped_dependency": # Don't show button if skipped due to upstream failure shown by pipeline
                    st.caption(f"Per eseguire '{agent_spec['button_label']}', completare prima: {', '.join(missing_prereqs)}")


# --- Refactored Page Functions ---
def single_requirement_page_refactored(client_gemini, global_model_selection):
    REQ_ID_SINGLE = "single_page_active_requirement"

    if 'single_page_requisito_text' not in st.session_state:
        st.session_state.single_page_requisito_text = ""

    st.session_state.single_page_requisito_text = st.text_area(
        "Inserisci il requisito:",
        value=st.session_state.single_page_requisito_text,
        key="text_area_single_page_req",
        height=120
    )
    current_requirement_text = st.session_state.single_page_requisito_text

    col_run_single, col_clear_single = st.columns(2)
    with col_run_single:
        if st.button("🚀 Esegui Analisi Completa (Singolo)", key="run_all_single_page", type="primary", use_container_width=True):
            if not current_requirement_text.strip():
                st.warning("Inserisci un requisito prima di eseguire l'analisi completa.")
            else:
                run_full_analysis_pipeline(REQ_ID_SINGLE, current_requirement_text, client_gemini, global_model_selection)
    with col_clear_single:
        if st.button("🧹 Svuota Risultati", key="clear_single_page", use_container_width=True):
            if REQ_ID_SINGLE in st.session_state.analysis_results:
                st.session_state.analysis_results[REQ_ID_SINGLE] = {}
            # st.session_state.single_page_requisito_text = "" # Optionally clear text
            st.rerun()

    if REQ_ID_SINGLE in st.session_state.analysis_results and st.session_state.analysis_results[REQ_ID_SINGLE]:
         render_unified_analysis_tabs(REQ_ID_SINGLE, current_requirement_text, client_gemini, global_model_selection)
    elif not current_requirement_text.strip():
        st.info("Inserisci un requisito e clicca 'Esegui Analisi Completa'.")


def jira_integration_page_refactored(client_gemini, global_model_selection):
    jira_instance = get_jira_instance()
    if not jira_instance: return  # Errore già gestito

    projects = get_jira_projects(jira_instance)
    if not projects: return

    # Sidebar per selezione progetto e tipo issue
    st.sidebar.title("Configurazione Jira")
    selected_project_key = st.sidebar.selectbox(
        "Seleziona Progetto Jira",
        options=list(projects.keys()),
        format_func=projects.get,
        key="jira_project_selector"
    )

    issue_types_options = ["Epic", "Story", "Task", "Bug"]
    selected_issue_types = st.sidebar.multiselect(
        "Seleziona Tipi di Issue",
        options=issue_types_options,
        default=["Story"],
        key="jira_issue_type_selector"
    )

    if not selected_project_key or not selected_issue_types:
        st.info("Seleziona un progetto e almeno un tipo di issue dalla sidebar.")
        return

    issues = get_project_issues(jira_instance, selected_project_key, tuple(selected_issue_types))

    # Stato locale per mappare le selezioni
    if 'jira_selected_issue_map' not in st.session_state:
        st.session_state.jira_selected_issue_map = {}

    st.subheader("Issue Trovate nel Progetto Selezionato")
    if issues:
        selected_keys_for_analysis = []
        cols = st.columns(3)
        for i, issue_data in enumerate(issues):
            col = cols[i % 3]
            issue_key = issue_data['key']
            is_selected = col.checkbox(
                f"{issue_key} - {issue_data['fields']['summary']}",
                key=f"jira_cb_{issue_key}",
                value=(issue_key in st.session_state.jira_selected_issue_map)
            )
            if is_selected:
                selected_keys_for_analysis.append(issue_key)
                st.session_state.jira_selected_issue_map[issue_key] = issue_data
            elif issue_key in st.session_state.jira_selected_issue_map:
                del st.session_state.jira_selected_issue_map[issue_key]

            with col.expander("Dettagli Brevi"):
                desc = issue_data['fields']['description']
                st.markdown(f"**Descrizione:** {desc[:300]}..." if desc else "Nessuna descrizione.")

        # Inizializza coda batch se non esiste
        if 'jira_batch_queue' not in st.session_state:
            st.session_state.jira_batch_queue = []
        if 'jira_batch_index' not in st.session_state:
            st.session_state.jira_batch_index = 0

        # Esegui analisi su tutte le selezionate
        if st.button(f"🚀 Esegui Analisi per {len(st.session_state.jira_selected_issue_map)} Issue Selezionate", key="run_all_jira", type="primary", disabled=not st.session_state.jira_selected_issue_map):
            st.session_state.jira_batch_queue = [
                (f"jira_issue_{issue_k}", issue_d['fields'].get('description', ""))
                for issue_k, issue_d in st.session_state.jira_selected_issue_map.items()
            ]
            st.session_state.jira_batch_index = 0
            st.rerun()

        # Pulsante per pulizia
        if st.sidebar.button("🧹 Svuota Risultati", key="clear_selected_jira_results", disabled=not st.session_state.jira_selected_issue_map):
            for issue_k in list(st.session_state.jira_selected_issue_map.keys()):
                req_id = f"jira_issue_{issue_k}"
                if req_id in st.session_state.analysis_results:
                    del st.session_state.analysis_results[req_id]
            st.rerun()

        # Visualizza risultati disponibili
        if st.session_state.jira_selected_issue_map:
            st.markdown("---")
            st.subheader("Risultati Analisi per Issue Selezionate")
        for issue_k, issue_data in st.session_state.jira_selected_issue_map.items():
            req_id = f"{issue_k}"
            if req_id in st.session_state.analysis_results and st.session_state.analysis_results[req_id]:
                with st.expander(f"Analisi per {issue_k} - {issue_data['fields']['summary']}", expanded=True):
                    description = issue_data['fields'].get('description', "")
                    render_unified_analysis_tabs(req_id, description, client_gemini, global_model_selection)

    else:
        st.info("Nessuna issue trovata per i criteri selezionati.")
        st.session_state.jira_selected_issue_map = {}

    # Esecuzione batch queue
    if st.session_state.get("jira_batch_queue"):
        jira_queue = st.session_state["jira_batch_queue"]
        idx = st.session_state.get("jira_batch_index", 0)

        if idx < len(jira_queue):
            req_id, desc = jira_queue[idx]

            # Mostra uno spinner per l'elemento corrente
            with st.spinner(f"Elaborazione '{req_id}' ({idx + 1}/{len(jira_queue)})..."):
                run_full_analysis_pipeline(req_id, desc, client_gemini, global_model_selection)

            st.session_state.jira_batch_index += 1
            st.rerun() # Passa all'elemento successivo o rifletti lo stato
        else:
            st.success("Tutte le issue Jira selezionate sono state elaborate.")
            st.session_state.jira_batch_queue = []
            st.session_state.jira_batch_index = 0
            st.rerun() # Rerun finale per pulire e mostrare il messaggio di successo


def multiple_requirements_page_refactored(client_gemini, global_model_selection):
    SESSION_KEY_MULTI_REQS_LIST = "multi_page_req_list_texts"
    MULTI_REQ_ID_PREFIX = "multi_item_analysis_"
    SESSION_KEY_MULTI_BATCH_QUEUE = "multi_req_batch_queue"
    SESSION_KEY_MULTI_BATCH_INDEX = "multi_req_batch_index"

    if SESSION_KEY_MULTI_REQS_LIST not in st.session_state:
        st.session_state[SESSION_KEY_MULTI_REQS_LIST] = [""]
    if SESSION_KEY_MULTI_BATCH_QUEUE not in st.session_state:
        st.session_state[SESSION_KEY_MULTI_BATCH_QUEUE] = []
    if SESSION_KEY_MULTI_BATCH_INDEX not in st.session_state:
        st.session_state[SESSION_KEY_MULTI_BATCH_INDEX] = 0

    st.subheader("Inserisci Requisiti Multipli")

    req_list_copy = list(st.session_state[SESSION_KEY_MULTI_REQS_LIST])
    for i in range(len(req_list_copy)):
        cols_multi_req_input = st.columns([10, 1])
        st.session_state[SESSION_KEY_MULTI_REQS_LIST][i] = cols_multi_req_input[0].text_area(
            f"Requisito {i+1}",
            value=req_list_copy[i],
            key=f"multi_req_text_area_item_{i}",
            height=80
        )
        if cols_multi_req_input[1].button("➖", key=f"remove_multi_req_item_{i}"):
            if len(st.session_state[SESSION_KEY_MULTI_REQS_LIST]) > 1:
                st.session_state[SESSION_KEY_MULTI_REQS_LIST].pop(i)
                req_id_to_remove = f"{MULTI_REQ_ID_PREFIX}{i}" # La logica di rimozione potrebbe necessitare di aggiustamenti per ID stabili
                if req_id_to_remove in st.session_state.analysis_results:
                    del st.session_state.analysis_results[req_id_to_remove]
                # Rimuovi anche dalla coda batch se presente
                st.session_state[SESSION_KEY_MULTI_BATCH_QUEUE] = [
                    item for item_idx, item in enumerate(st.session_state[SESSION_KEY_MULTI_BATCH_QUEUE])
                    if item[0] != req_id_to_remove # item è una tupla (req_id, req_text)
                ]
                if st.session_state[SESSION_KEY_MULTI_BATCH_INDEX] >= len(st.session_state[SESSION_KEY_MULTI_BATCH_QUEUE]):
                     st.session_state[SESSION_KEY_MULTI_BATCH_INDEX] = 0 if st.session_state[SESSION_KEY_MULTI_BATCH_QUEUE] else 0


                st.rerun()
                return

    if st.button("➕ Aggiungi Campo Requisito", key="add_multi_req_field"):
        st.session_state[SESSION_KEY_MULTI_REQS_LIST].append("")
        st.rerun()

    st.markdown("---")
    col_run_multi, col_clear_multi = st.columns(2)
    with col_run_multi:
        if st.button("🚀 Esegui Analisi per Tutti i Requisiti (Multi)", key="run_all_multi_page", type="primary", use_container_width=True, disabled=bool(st.session_state.get(SESSION_KEY_MULTI_BATCH_QUEUE))):
            valid_reqs_to_process = [
                (f"{MULTI_REQ_ID_PREFIX}{i}", req_text)
                for i, req_text in enumerate(st.session_state[SESSION_KEY_MULTI_REQS_LIST])
                if req_text.strip()
            ]
            if not valid_reqs_to_process:
                st.warning("Inserisci almeno un requisito valido prima di eseguire l'analisi.")
            else:
                st.session_state[SESSION_KEY_MULTI_BATCH_QUEUE] = valid_reqs_to_process
                st.session_state[SESSION_KEY_MULTI_BATCH_INDEX] = 0
                st.rerun() # Avvia l'elaborazione della coda
    with col_clear_multi:
        if st.button("🧹 Svuota i Risultati", key="clear_multi_page_all", use_container_width=True):
            st.session_state[SESSION_KEY_MULTI_REQS_LIST] = [""]
            keys_to_delete = [k for k in st.session_state.analysis_results if k.startswith(MULTI_REQ_ID_PREFIX)]
            for k_del in keys_to_delete:
                del st.session_state.analysis_results[k_del]
            st.session_state[SESSION_KEY_MULTI_BATCH_QUEUE] = []
            st.session_state[SESSION_KEY_MULTI_BATCH_INDEX] = 0
            st.rerun()

    # Logica di elaborazione batch per requisiti multipli
    if st.session_state.get(SESSION_KEY_MULTI_BATCH_QUEUE):
        batch_queue = st.session_state[SESSION_KEY_MULTI_BATCH_QUEUE]
        idx = st.session_state.get(SESSION_KEY_MULTI_BATCH_INDEX, 0)

        if idx < len(batch_queue):
            req_id_multi, req_text_multi = batch_queue[idx]

            # Mostra uno spinner per l'elemento corrente
            with st.spinner(f"Elaborazione requisito '{req_id_multi}' ({idx + 1}/{len(batch_queue)})..."):
                run_full_analysis_pipeline(req_id_multi, req_text_multi, client_gemini, global_model_selection)

            st.session_state[SESSION_KEY_MULTI_BATCH_INDEX] += 1
            st.rerun() # Passa all'elemento successivo o rifletti lo stato
        else:
            st.success("Tutti i requisiti multipli sono stati elaborati.")
            st.session_state[SESSION_KEY_MULTI_BATCH_QUEUE] = []
            st.session_state[SESSION_KEY_MULTI_BATCH_INDEX] = 0
            st.rerun() # Rerun finale per pulire e mostrare il messaggio di successo

    st.markdown("---")
    st.subheader("Risultati Analisi per Requisito")
    for i, req_text_display in enumerate(st.session_state[SESSION_KEY_MULTI_REQS_LIST]):
        req_id_multi_display = f"{MULTI_REQ_ID_PREFIX}{i}"
        if req_text_display.strip() or (req_id_multi_display in st.session_state.analysis_results and st.session_state.analysis_results[req_id_multi_display]):
            with st.expander(f"Dettagli Analisi per Requisito {i+1}: {req_text_display[:60]}...", expanded=True):
                if not req_text_display.strip() and (req_id_multi_display not in st.session_state.analysis_results or not st.session_state.analysis_results[req_id_multi_display]):
                    st.caption(f"Requisito {i+1} è vuoto.")
                elif req_id_multi_display in st.session_state.analysis_results and st.session_state.analysis_results[req_id_multi_display]:
                    render_unified_analysis_tabs(req_id_multi_display, req_text_display, client_gemini, global_model_selection)
                else:
                    st.info(f"Nessuna analisi eseguita per Requisito {i+1}. Premi 'Esegui Analisi per Tutti'.")


def main():
    st.title("🤖 (TEST)INA")

    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}

    client_gemini = get_genai_client()
    if not client_gemini:
        st.error("Client Gemini non inizializzato. Controlla la chiave API e la configurazione.")
        return # Stop execution if client is not available

    # Selezione del modello globale nella Sidebar
    st.sidebar.title("Configurazione Globale")
    global_model_selection = st.sidebar.selectbox(
        "Seleziona Modello Gemini (Globale):",
        options=["gemini-2.0-flash-001", "gemini-1.5-flash-latest"], # Add more models
        index=0, # Default to flash
        key="global_model_selector"
    )


    page_options = {
        "📝 Requisito Singolo": lambda: single_requirement_page_refactored(client_gemini, global_model_selection),
        "📄 Requisiti Multipli": lambda: multiple_requirements_page_refactored(client_gemini, global_model_selection),
        "🔗 Integrazione Jira": lambda: jira_integration_page_refactored(client_gemini, global_model_selection)
    }
        
    # Selezione modalità via Sidebar
    st.sidebar.markdown("---")
    selected_page_name = st.sidebar.radio("Modalità Operativa:", list(page_options.keys()), label_visibility="visible")


    # Mostra la pagina selezionata
    page_to_render_func = page_options[selected_page_name]
    page_to_render_func()

if __name__ == "__main__":
    main()
