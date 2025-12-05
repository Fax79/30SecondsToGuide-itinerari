import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64
import datetime
import unicodedata
import os

# --- CONFIGURAZIONE PAGINA ---
if os.path.exists("logo.png"):
    st.set_page_config(page_title="Itinerary Wizard", page_icon="logo.png", layout="centered")
else:
    st.set_page_config(page_title="Itinerary Wizard", page_icon="🧙‍♂️", layout="centered")

# --- MEMORIA & API ---
@st.cache_resource
def get_shared_logs():
    return [] 

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("⚠️ Chiave API mancante! Inseriscila nei 'Secrets'.")
    st.stop()

# ==========================================
# 💰 AREA MONETIZZAZIONE (Identica alla Home)
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

# --- LINK PROMOZIONE ---
PROMO_LINK = "https://www.30secondstoguide.it" 

# --- Funzione Helper per Bottoni con Logo ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

def partner_button(label, link, image_file):
    if os.path.exists(image_file):
        try:
            img_base64 = get_base64_of_bin_file(image_file)
            html_code = f"""
            <a href="{link}" target="_blank">
                <img src="data:image/png;base64,{img_base64}" style="width:100%; border-radius:8px; border: 1px solid #e0e0e0; transition: transform 0.2s;">
            </a>
            <div style="text-align: center; margin-top: 5px; margin-bottom: 15px;">
                <a href="{link}" target="_blank" style="text-decoration: none; color: #E67E22; font-weight: bold; font-size: 0.9em;">{label} ➜</a>
            </div>
            """
            st.markdown(html_code, unsafe_allow_html=True)
        except:
            st.link_button(label, link, use_container_width=True)
    else:
        st.link_button(label, link, use_container_width=True)

# ==========================================
# 🧙‍♂️ PDF ENGINE "WIZARD EDITION"
# ==========================================
def create_complex_pdf(text, destination, meta_data):
    
    # --- FUNZIONE SPAZZINO 4.0 (EURO FIX BLINDATO) ---
    def clean_text_for_pdf(text_input):
        if not text_input: return ""
        
        # 1. Sostituzione preventiva SIMBOLI CRITICI
        # Il simbolo Euro (€) DEVE diventare EUR prima di ogni altra cosa per evitare crash
        replacements = {
            "€": "EUR", "â¬": "EUR", # Euro e varianti encoding
            "$": "USD", "£": "GBP",
            "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."
        }
        for char, replacement in replacements.items():
            text_input = text_input.replace(char, replacement)
            
        # 2. Normalizzazione NFC (Compatta gli accenti italiani: à resta à)
        text_input = unicodedata.normalize('NFC', text_input)
        
        output = []
        for char in text_input:
            try:
                # 3. Test Latin-1: Se passa (es. à, è, o testo normale), lo teniamo.
                char.encode('latin-1')
                output.append(char)
            except UnicodeEncodeError:
                # 4. Fallback: Se non passa (es. Č), normalizziamo a base ASCII (C)
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
            # Pulizia preventiva anche qui sui metadati (soprattutto budget con simbolo Euro)
            clean_budget = clean_text_for_pdf(meta['budget'])
            self.cell(0, 6, f"Date: {meta['dates']}", 0, 1, 'C')
            self.cell(0, 6, f"Viaggiatori: {meta['pax']}", 0, 1, 'C')
            self.cell(0, 6, f"Budget Target: {clean_budget}", 0, 1, 'C')
            
            self.set_y(260)
            self.set_font('Helvetica', '', 10)
            self.cell(0, 10, "GENERATO CON www.30secondstoguide.it", 0, 0, 'C', link="https://www.30secondstoguide.it")

    pdf = WizardPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.make_cover(dest_clean, meta_data)
    pdf.add_page()
    
    # --- BOX CONTESTUALE ---
    def make_box(pdf_obj, text, link, color="blue"):
        text = clean_text_for_pdf(text) # Pulizia obbligatoria anche qui
        colors = {
            "blue": (235, 245, 255), "green": (240, 255, 240),
            "yellow": (255, 252, 235), "orange": (255, 245, 235),
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
        pdf_obj.cell(180, 6, f"> {text}", link=link)
        pdf_obj.ln(14)

    lines = text.split('\n')
    
    for line in lines:
        clean_line = clean_text_for_pdf(line)
        
        # --- TRIGGER CONTESTUALI ---
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

        if line.strip().startswith('# '): 
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 20)
            pdf.set_text_color(44, 62, 80)
            pdf.multi_cell(0, 10, clean_line.replace('#', '').strip())
            pdf.ln(5)
            
        elif line.strip().startswith('## '): 
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(230, 126, 34) 
            pdf.multi_cell(0, 10, clean_line.replace('##', '').strip())
            
        elif line.strip().startswith('**') and 'VERDETTO' in line.upper(): 
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 12)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(0, 10, clean_line.replace('**', ''), 1, 1, 'C', fill=True)
            pdf.ln(5)
            
        elif line.strip().startswith('* ') or line.strip().startswith('- '): 
            pdf.set_font("Helvetica", '', 11)
            pdf.set_text_color(20, 20, 20)
            pdf.set_x(15)
            pdf.cell(5, 6, chr(149), 0, 0)
            pdf.multi_cell(0, 6, clean_line.replace('* ', '').replace('- ', ''))
            
        else: 
            if line.strip():
                pdf.set_font("Helvetica", '', 11)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(0, 6, clean_line.replace('**', ''))
                pdf.ln(1)

    # --- PAGINA PARTNER FINALE ---
    pdf.add_page()
    
    def make_sponsor_box(title, subtitle, link, highlight=False):
        title = clean_text_for_pdf(title)
        subtitle = clean_text_for_pdf(subtitle)
        if highlight:
            pdf.set_fill_color(230, 240, 255) 
            pdf.set_draw_color(0, 102, 204)   
        else:
            pdf.set_fill_color(250, 250, 250) 
            pdf.set_draw_color(220, 220, 220) 
        start_y = pdf.get_y()
        pdf.rect(10, start_y, 190, 14, 'DF') 
        pdf.set_y(start_y + 2)
        pdf.set_x(15)
        pdf.set_font("Helvetica", 'B', 10) 
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 5, title, 0, 1)
        pdf.set_x(15)
        pdf.set_font("Helvetica", '', 9)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 6, subtitle, 0, 1, link=link)
        pdf.ln(4) 

    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Già visti nella guida...", 0, 1, 'L')
    pdf.ln(2)
    make_sponsor_box("Booking.com", "Hotel e alloggi", HOTEL_LINK)
    make_sponsor_box("Tiqets", "Biglietti musei e attrazioni", TIQETS_LINK) 
    make_sponsor_box("Kiwi.com", "Voli low cost", FLIGHT_LINK)
    make_sponsor_box("Heymondo", "Assicurazione viaggio", INSURANCE_LINK)
    make_sponsor_box("Saily", "eSim internazionale", ESIM_LINK)
    make_sponsor_box("Welcome Pickups", "Transfer aeroportuali", TRANSF_LINK)

    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(44, 62, 80) 
    pdf.cell(0, 10, "ALTRI SERVIZI INDISPENSABILI", 0, 1, 'L')
    pdf.ln(2)
    make_sponsor_box("Deposito Bagagli", "Libera le mani con Radical Storage", LUGGAGE_LINK, highlight=True)
    make_sponsor_box("Rimborsi Voli", "Volo in ritardo? Chiedi risarcimento con AirHelp", REIMB_LINK, highlight=True)
    make_sponsor_box("Noleggio Auto", "Migliori tariffe con Auto Europe", RENTAL_LINK, highlight=True)
    make_sponsor_box("Treni e Bus", "Prenota con Omio", TRAIN_LINK, highlight=True)
    make_sponsor_box("Taxi Locale", "Kiwitaxi per spostamenti urbani", TAXI_LINK, highlight=True)
    make_sponsor_box("Ristoranti", "Recensioni su TripAdvisor", RESTAURANT_LINK, highlight=True)

    return bytes(pdf.output(dest='S'))

# ==========================================
# 🖥️ INTERFACCIA WIZARD (UI Home Page Clone)
# ==========================================

# --- SIDEBAR IDENTICA ALLA PRINCIPALE ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.title("⏱️")
    
    st.markdown("---")
    st.caption("✈️ PRENOTAZIONI")
    partner_button("Voli (Kiwi)", FLIGHT_LINK, "btn_kiwi.png")
    partner_button("Hotel (Booking)", HOTEL_LINK, "btn_booking.png")
    partner_button("Transfers (Welcome)", TRANSF_LINK, "btn_wp.png")
    partner_button("Auto (Autoeurope)", RENTAL_LINK, "btn_autoe.png")
    partner_button("Treni (Omio)", TRAIN_LINK, "btn_omio.png")
    partner_button("Taxi (Kiwitaxi)", TAXI_LINK, "btn_taxi.png")
    
    st.caption("🎟️ ESPERIENZE & ALTRO")
    partner_button("Musei & Ticket (Tiqets)", TIQETS_LINK, "btn_tiqets.png") 
    partner_button("Ristoranti (Tripadvisor)", RESTAURANT_LINK, "btn_tripadv.png")
    
    st.caption("🛠️ SERVIZI UTILI")
    partner_button("eSim (Saily)", ESIM_LINK, "btn_saily.png")
    partner_button("Bagagli (Radical)", LUGGAGE_LINK, "btn_radical.png")
    partner_button("Polizza (Heymondo)", INSURANCE_LINK, "btn_heymondo.png")
    partner_button("Rimborsi (Airhelp)", REIMB_LINK, "btn_airhelp.png")
    
    # --- AREA ADMIN SEGRETA ---
    with st.sidebar.expander("🔐 Admin Stats"):
        secret_pwd = st.text_input("Password", type="password")
        if secret_pwd == "fabio123": 
            st.write("### 📊 Ultime Ricerche:")
            logs = get_shared_logs()
            if logs:
                for log in reversed(logs):
                    st.caption(log)
            else:
                st.caption("Nessuna ricerca ancora.")
            st.write(f"**Totale:** {len(logs)}")

    st.markdown("---")
    st.caption("© 2025 30SecondsToGuide")

# --- CORPO CENTRALE (Header Identico) ---
if os.path.exists("logo.png"):
    col_sp1, col_img, col_sp2 = st.columns([3, 2, 3])
    with col_img:
        st.image("logo.png", use_container_width=True)

st.markdown("""
    <h1 style='text-align: center; color: #2C3E50; margin-bottom: 0; margin-top: -10px;'>
        Itinerary Wizard
    </h1>
    <p style='text-align: center; color: #E67E22; font-size: 1.2em; font-style: italic; margin-top: 5px;'>
        Il pianificatore di viaggi complessi con analisi del budget.
    </p>
    """, unsafe_allow_html=True)

st.write("") 

# --- INPUT FORM WIZARD (Al posto del campo città semplice) ---
with st.container():
    st.info("🧙‍♂️ Inserisci i dettagli per ricevere un Manuale Operativo completo.")
    
    c1, c2 = st.columns(2)
    with c1:
        destination = st.text_input("Destinazione (Regione/Paese)", placeholder="Es. Giappone, Irlanda...")
        start_date = st.date_input("Data Partenza", datetime.date.today() + datetime.timedelta(days=30))
        adults = st.number_input("Numero Adulti", min_value=1, value=2)
        
    with c2:
        budget = st.number_input("Budget Totale (€)", min_value=500, value=3000, step=100)
        end_date = st.date_input("Data Ritorno", datetime.date.today() + datetime.timedelta(days=37))
        kids = st.number_input("Numero Minorenni", min_value=0, value=0)

    # Età bambini dinamica
    kids_ages = []
    if kids > 0:
        st.caption("Età dei ragazzi:")
        k_cols = st.columns(min(kids, 4))
        for i in range(kids):
            with k_cols[i % 4]:
                age = st.number_input(f"Età figlio {i+1}", 0, 17, 10, key=f"kid_{i}")
                kids_ages.append(str(age))

    st.write("")
    
    # --- LOGICA BOTTONE RESET ---
    def reset_app():
        if 'wizard_pdf' in st.session_state:
            del st.session_state['wizard_pdf']
    
    is_generated = 'wizard_pdf' in st.session_state
    
    # Bottone Genera
    if st.button("✨ Crea il mio Manuale", type="primary", use_container_width=True, disabled=is_generated):
        if not destination:
            st.warning("Inserisci una destinazione!")
        else:
            duration = (end_date - start_date).days
            pax_desc = f"{adults} Adulti"
            if kids > 0: pax_desc += f", {kids} Ragazzi ({', '.join(kids_ages)} anni)"
            
            with st.spinner(f"🧙‍♂️ Sto elaborando l'itinerario per {destination}..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    prompt = f"""
                    Agisci come un Travel Planner Senior. Crea un "Manuale Operativo di Viaggio" per: {destination}.
                    
                    DATI:
                    - Durata: {duration} notti ({start_date} - {end_date})
                    - Gruppo: {pax_desc}
                    - Budget: € {budget}
                    
                    STRUTTURA TITOLI (Usa ESATTAMENTE questi):
                    # {destination.upper()}: [Sottotitolo]
                    **IL VERDETTO SUL BUDGET: € {budget}** (Stato: Sufficiente/Stretto/Impossibile)
                    ## CAPITOLO 1: LA PREPARAZIONE (Voli, eSim, Assicurazione)
                    ## CAPITOLO 2: DOVE DORMIRE (Strategie alloggio)
                    ## CAPITOLO 3: L'ITINERARIO GIORNO PER GIORNO (Dettagliato)
                    ## CAPITOLO 4: SOPRAVVIVENZA PRATICA (Cibo)
                    ## CAPITOLO 5: CONTO ECONOMICO FINALE
                    
                    REGOLE:
                    1. Usa EURO per i costi.
                    2. Sii onesto sul budget.
                    3. Niente tabelle markdown.
                    """
                    
                    response = model.generate_content(prompt)
                    text_content = response.text
                    
                    meta = {
                        "dates": f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m/%Y')}",
                        "pax": f"{adults} Ad + {kids} Bimbi",
                        "budget": f"€ {budget}"
                    }
                    
                    pdf_bytes = create_complex_pdf(text_content, destination, meta)
                    st.session_state['wizard_pdf'] = pdf_bytes
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Errore del Mago: {e}")

    # Bottone Scarica
    if 'wizard_pdf' in st.session_state:
        st.success("✅ Itinerario pronto!")
        st.download_button(
            label="📥 SCARICA IL MANUALE (PDF)",
            data=st.session_state['wizard_pdf'],
            file_name=f"Manuale_{destination.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            on_click=reset_app
        )

# =========================================================
# 🏨 TRAVEL HUB (Identico alla Home)
# =========================================================
st.markdown("---")
st.subheader("✈️ I migliori strumenti per il tuo viaggio")

# RIGA 1
c1, c2, c3 = st.columns(3)
with c1:
    st.caption("✈️ **Voli**")
    partner_button("Voli Kiwi", FLIGHT_LINK, "btn_kiwi.png")
with c2:
    st.caption("🏨 **Hotel**")
    partner_button("Booking", HOTEL_LINK, "btn_booking.png")
with c3:
    st.caption("🚘 **Transfer**")
    partner_button("Welcome Pickups", TRANSF_LINK, "btn_wp.png")

st.write("") 

# RIGA 2
c4, c5, c6 = st.columns(3)
with c4:
    st.caption("🎟️ **Tour**")
    partner_button("Tiqets", TIQETS_LINK, "btn_tiqets.png") 
with c5:
    st.caption("🚗 **Auto**")
    partner_button("Noleggio", RENTAL_LINK, "btn_autoe.png")
with c6:
    st.caption("🎒 **Bagagli**")
    partner_button("Deposito", LUGGAGE_LINK, "btn_radical.png")

st.write("") 

# RIGA 3
c7, c8, c9 = st.columns(3)
with c7:
    st.caption("📲 **Dati**")
    partner_button("eSim Saily", ESIM_LINK, "btn_saily.png")
with c8:
    st.caption("🛡️ **Polizza**")
    partner_button("Assicuraz.", INSURANCE_LINK, "btn_heymondo.png")
with c9:
    st.caption("💸 **Risarcim.**")
    partner_button("AirHelp", REIMB_LINK, "btn_airhelp.png")

st.write("") 

# RIGA 4
c10, c11, c12 = st.columns(3)
with c10:
    st.caption("🚆 **Treni**")
    partner_button("Omio", TRAIN_LINK, "btn_omio.png")
with c11:
    st.caption("🍴 **Ristoranti**")
    partner_button("Tripadvisor", RESTAURANT_LINK, "btn_tripadv.png")
with c12:
    st.caption("🚖 **Taxi**")
    partner_button("Kiwitaxi", TAXI_LINK, "btn_taxi.png")

# --- SEZIONE SEO ---
st.markdown("---")
st.markdown("""
<div style="text-align: justify; color: #555;">
    <h3>Come funziona Itinerary Wizard?</h3>
    <p>
        Questo strumento avanzato di <strong>30SecondsToGuide</strong> pianifica viaggi complessi analizzando il tuo budget.
        Inserisci destinazione, date, composizione del gruppo e budget massimo: l'AI genererà un 
        <strong>Manuale Operativo</strong> completo con strategie di spesa, itinerari giornalieri e consigli logistici.
    </p>
    <p>
        Il servizio è <strong>gratuito al 100%</strong>.
    </p>
</div>
""", unsafe_allow_html=True)
