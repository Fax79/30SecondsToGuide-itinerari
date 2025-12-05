import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64
import datetime
import unicodedata
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Itinerary Wizard | 30SecondsToGuide", page_icon="🧙‍♂️", layout="wide")

# --- MEMORIA & API ---
@st.cache_resource
def get_shared_logs():
    return [] 

try:
    # Gestione Secrets: Funziona sia in locale (secrets.toml) che su Streamlit Cloud
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("⚠️ Chiave API mancante! Inseriscila nei 'Secrets' di Streamlit Cloud.")
    st.stop()

# ==========================================
# 🔗 LINK AFFILIATI (STATICI)
# ==========================================
FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"
LUGGAGE_LINK = "https://radicalstorage.tpx.lt/fpjMovNW"
REIMB_LINK = "https://airhelp.tpx.lt/YS9ciIsW"
ESIM_LINK = "https://saily.tpx.lt/Myxhqmox"
RENTAL_LINK = "https://autoeurope.tpx.lt/73PS7HAR"
TRANSF_LINK = "https://tpx.lt/O5I4OrpX"
TAXI_LINK = "https://kiwitaxi.tpx.lt/KCeVs32Q"
TIQETS_LINK = "https://tiqets.tpx.lt/XV1Urbnn"
INSURANCE_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=INPUT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
TRAIN_LINK = "https://www.omio.com"
RESTAURANT_LINK = "https://www.tripadvisor.com"
HOTEL_LINK = "https://www.booking.com"
TOUR_LINK = "https://www.getyourguide.com"

# --- HELPER IMMAGINI ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# ==========================================
# 🧙‍♂️ PDF ENGINE "WIZARD EDITION"
# ==========================================
def create_complex_pdf(text, destination, meta_data):
    
    # 1. Spazzino Intelligente (Versione 3.6 - Italiana)
    def clean_text_for_pdf(text_input):
        if not text_input: return ""
        text_input = unicodedata.normalize('NFC', text_input)
        replacements = {
            "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "...",
            "€": "EUR", "$": "USD", "£": "GBP"
        }
        for char, replacement in replacements.items():
            text_input = text_input.replace(char, replacement)
        output = []
        for char in text_input:
            try:
                char.encode('latin-1')
                output.append(char)
            except UnicodeEncodeError:
                decomposed = unicodedata.normalize('NFD', char)
                stripped = "".join(c for c in decomposed if unicodedata.category(c) != 'Mn')
                output.append(stripped)
        return "".join(output)

    dest_clean = clean_text_for_pdf(destination)

    class WizardPDF(FPDF):
        def header(self):
            if self.page_no() == 1: return
            self.set_fill_color(44, 62, 80) 
            self.rect(0, 0, 210, 15, 'F')
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(255, 255, 255)
            self.set_y(6)
            self.cell(0, 0, f'MANUALE OPERATIVO: {dest_clean.upper()}', 0, 0, 'R')
            self.ln(15) 
            
        def footer(self):
            self.set_draw_color(200, 200, 200)
            self.line(10, 285, 200, 285)
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'30SecondsToGuide - Pagina {self.page_no()}', 0, 0, 'C')

        def make_cover(self, dest, meta):
            self.add_page()
            # Sfondo Elegante
            self.set_fill_color(245, 245, 245) 
            self.rect(0, 0, 210, 297, 'F') 
            
            # Logo
            if os.path.exists("logo.png"):
                self.image("logo.png", x=80, y=30, w=50)
            
            self.ln(80)
            self.set_font('Helvetica', 'B', 36)
            self.set_text_color(44, 62, 80)
            self.multi_cell(0, 15, dest.upper(), align='C')
            
            self.ln(10)
            self.set_font('Helvetica', 'I', 14)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, "Manuale Operativo di Viaggio", 0, 1, 'C')
            
            # Box Dati Viaggio
            self.ln(20)
            self.set_fill_color(255, 255, 255)
            self.rect(55, 140, 100, 50, 'F')
            
            self.set_y(145)
            self.set_font('Helvetica', 'B', 10)
            self.cell(0, 6, f"Date: {meta['dates']}", 0, 1, 'C')
            self.cell(0, 6, f"Viaggiatori: {meta['pax']}", 0, 1, 'C')
            self.cell(0, 6, f"Budget Target: {meta['budget']}", 0, 1, 'C')
            
            self.set_y(260)
            self.set_font('Helvetica', '', 10)
            self.cell(0, 10, "GENERATO CON www.30secondstoguide.it", 0, 0, 'C', link="https://www.30secondstoguide.it")

    pdf = WizardPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.make_cover(dest_clean, meta_data)
    pdf.add_page()
    
    # --- BOX CONTESTUALE ---
    def make_box(pdf_obj, text, link, color="blue"):
        # Colori pastello professionali
        colors = {
            "blue": (235, 245, 255),
            "green": (240, 255, 240),
            "yellow": (255, 252, 235),
            "orange": (255, 245, 235),
            "gray": (245, 245, 245)
        }
        r, g, b = colors.get(color, (245,245,245))
        
        pdf_obj.ln(3)
        pdf_obj.set_fill_color(r, g, b)
        pdf_obj.set_draw_color(r-10, g-10, b-10)
        pdf_obj.rect(10, pdf_obj.get_y(), 190, 12, 'DF')
        
        pdf_obj.set_xy(15, pdf_obj.get_y() + 3)
        pdf_obj.set_font("Helvetica", 'B', 9)
        pdf_obj.set_text_color(44, 62, 80)
        pdf_obj.cell(180, 6, f"> {clean_text_for_pdf(text)}", link=link)
        pdf_obj.ln(14)

    lines = text.split('\n')
    
    for line in lines:
        clean_line = clean_text_for_pdf(line)
        
        # --- TRIGGER CONTESTUALI (Basati sui Capitoli del Prompt) ---
        if "CAPITOLO 1: LA PREPARAZIONE" in clean_line.upper():
            make_box(pdf, "Prenota i voli migliori su Kiwi.com (Multitratta)", FLIGHT_LINK, "gray")
            make_box(pdf, "eSim Saily: Internet immediato all'arrivo", ESIM_LINK, "green")
            make_box(pdf, "Assicurazione Sanitaria: Sconto 10% Heymondo", INSURANCE_LINK, "yellow")
            
        if "CAPITOLO 2: DOVE DORMIRE" in clean_line.upper():
            make_box(pdf, f"Verifica disponibilita Hotel a {dest_clean} su Booking.com", HOTEL_LINK, "blue")
            
        if "CAPITOLO 3:" in clean_line.upper() or "ITINERARIO" in clean_line.upper():
            make_box(pdf, f"Noleggio Auto: Confronta prezzi con Auto Europe", RENTAL_LINK, "gray")
            
        if "CAPITOLO 4:" in clean_line.upper() or "INFO PRATICHE" in clean_line.upper():
             make_box(pdf, f"Biglietti Musei e Attrazioni a {dest_clean} su Tiqets", TIQETS_LINK, "orange")

        # Formattazione Testo
        if line.strip().startswith('# '): # Titolo H1
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 20)
            pdf.set_text_color(44, 62, 80)
            pdf.multi_cell(0, 10, clean_line.replace('#', '').strip())
            pdf.ln(5)
            
        elif line.strip().startswith('## '): # Titolo H2
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(230, 126, 34) # Arancione Brand
            pdf.multi_cell(0, 10, clean_line.replace('##', '').strip())
            
        elif line.strip().startswith('**') and 'VERDETTO' in line.upper(): # Verdetto Budget
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 12)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(0, 10, clean_line.replace('**', ''), 1, 1, 'C', fill=True)
            pdf.ln(5)
            
        elif line.strip().startswith('* ') or line.strip().startswith('- '): # Elenchi
            pdf.set_font("Helvetica", '', 11)
            pdf.set_text_color(20, 20, 20)
            pdf.set_x(15)
            pdf.cell(5, 6, chr(149), 0, 0)
            pdf.multi_cell(0, 6, clean_line.replace('* ', '').replace('- ', ''))
            
        else: # Testo normale
            if line.strip():
                pdf.set_font("Helvetica", '', 11)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(0, 6, clean_line.replace('**', ''))
                pdf.ln(1)

    return bytes(pdf.output(dest='S'))

# ==========================================
# 🖥️ INTERFACCIA WIZARD
# ==========================================

st.markdown("""
# 🧙‍♂️ Itinerary Wizard (Beta)
*Generatore di Itinerari Complessi per Regioni/Nazioni*
""")

col1, col2 = st.columns([1, 2])

with col1:
    st.write("### 1. Dati Viaggio")
    destination = st.text_input("Destinazione (Paese o Regione)", placeholder="Es. Giappone, Irlanda, Toscana...")
    
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        start_date = st.date_input("Partenza", datetime.date.today() + datetime.timedelta(days=30))
    with d_col2:
        end_date = st.date_input("Ritorno", datetime.date.today() + datetime.timedelta(days=37))
        
    duration = (end_date - start_date).days
    st.caption(f"Durata: {duration} notti")
    
    st.write("### 2. Chi parte?")
    adults = st.number_input("Adulti", min_value=1, value=2)
    kids = st.number_input("Minorenni", min_value=0, value=0)
    
    kids_ages = []
    if kids > 0:
        st.caption("Età dei ragazzi:")
        k_cols = st.columns(min(kids, 4)) # Max 4 colonne per estetica
        for i in range(kids):
            with k_cols[i % 4]:
                age = st.number_input(f"Figlio {i+1}", 0, 17, 10, key=f"kid_{i}")
                kids_ages.append(str(age))
    
    st.write("### 3. Il Limite")
    budget = st.number_input("Budget Totale (€)", min_value=500, value=3000, step=100)
    
    generate_btn = st.button("✨ Crea Magia", type="primary", use_container_width=True)

with col2:
    if generate_btn:
        if not destination:
            st.error("Inserisci una destinazione!")
        else:
            # LOGGING
            pax_desc = f"{adults} Adulti"
            if kids > 0: pax_desc += f", {kids} Ragazzi ({', '.join(kids_ages)} anni)"
            
            with st.spinner(f"🧙‍♂️ Il Mago sta pianificando il viaggio in {destination} per {duration} giorni..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    # --- IL PROMPT KILLER ---
                    prompt = f"""
                    Agisci come un Travel Planner Senior e Consulente Finanziario esperto.
                    Devi creare un "Manuale Operativo di Viaggio" dettagliato per: {destination}.
                    
                    DATI INPUT:
                    - Durata: {duration} notti ({start_date} - {end_date})
                    - Gruppo: {pax_desc}
                    - Budget Totale TASSATIVO: € {budget}
                    
                    STRUTTURA OBBLIGATORIA (Usa esattamente questi titoli):
                    
                    # {destination.upper()}: [Sottotitolo Evocativo ed Estetico]
                    
                    [Intro evocativa di 10 righe sull'atmosfera del luogo in quel periodo]
                    
                    **IL VERDETTO SUL BUDGET: € {budget}**
                    Stato: [Sufficiente / Stretto / Impossibile]. 
                    [Spiegazione brutale ma onesta di cosa si può fare e cosa no. Applica la regola del "Lusso Selettivo": dove spendere, dove tagliare].
                    
                    ## CAPITOLO 1: LA PREPARAZIONE (I Pilastri)
                    1. Voli: Strategie per risparmiare (scali, aeroporti secondari). Stima costo.
                    2. Connessione: Consiglia eSIM. Stima costo.
                    3. Assicurazione: Consiglia polizza sanitaria. Stima costo.
                    
                    ## CAPITOLO 2: DOVE DORMIRE (Logistica)
                    Budget stimato per gli alloggi: € [Totale].
                    Consigli tattici su dove alloggiare per risparmiare (quartieri periferici, tipologie B&B/Ostelli design).
                    
                    ## CAPITOLO 3: L'ITINERARIO GIORNO PER GIORNO (La Bibbia)
                    [Scrivi un itinerario dettagliato per {duration} giorni.
                    NON fare un elenco puntato noioso. Racconta l'esperienza.
                    Cita luoghi specifici, momenti della giornata (tramonto, alba), esperienze sensoriali.
                    Per ogni tappa importante, specifica se è gratis o a pagamento.]
                    
                    ## CAPITOLO 4: SOPRAVVIVENZA PRATICA (Cibo)
                    Budget Cibo stimato: € [Totale].
                    Strategie per mangiare bene senza spendere troppo (Street food, mercati, supermercati locali, pranzi al sacco).
                    
                    ## CAPITOLO 5: CONTO ECONOMICO FINALE
                    [Crea una tabella di sintesi delle spese stimate per rientrare nel budget o spiegare perché si sfora].
                    
                    REGOLE DI SCRITTURA:
                    1. Tono: Autorevole, Pratico, Leggermente poetico (stile Reportage).
                    2. NO TABELLE MARKDOWN (Usa elenchi o testo discorsivo per il conto economico).
                    3. Usa caratteri standard (evita emoji nel testo principale per compatibilità PDF).
                    4. Sii specifico sui costi (usa €).
                    """
                    
                    response = model.generate_content(prompt)
                    text_content = response.text
                    
                    # Creazione Meta-Dati per Copertina
                    meta = {
                        "dates": f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m/%Y')}",
                        "pax": f"{adults} Ad + {kids} Bimbi",
                        "budget": f"€ {budget}"
                    }
                    
                    pdf_bytes = create_complex_pdf(text_content, destination, meta)
                    
                    st.success("✨ Itinerario Pronto!")
                    st.download_button(
                        label="📥 SCARICA IL MANUALE (PDF)",
                        data=pdf_bytes,
                        file_name=f"Guida_Wizard_{destination}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    # Preview Testuale (Opzionale)
                    with st.expander("📖 Leggi Anteprima"):
                        st.markdown(text_content)
                        
                except Exception as e:
                    st.error(f"Errore del Mago: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("Ambiente di Test - Modulo Itinerari Complessi v1.0")