import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Who Am I: Engine (BETA)",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS (Wygląd) ---
st.markdown("""
<style>
    .metric-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 10px; }
    .highlight { color: #2e86c1; font-weight: bold; }
    .success-box { background-color: #d4edda; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; color: #155724; }
    .warning-box { background-color: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107; color: #856404; }
    .info-box { background-color: #d1ecf1; padding: 15px; border-radius: 10px; border-left: 5px solid #17a2b8; color: #0c5460; }
</style>
""", unsafe_allow_html=True)

# --- 2. WARSTWA DANYCH (DATA LAYER) ---
@st.cache_data
def load_data():
    """Ładuje pliki CSV z repozytorium i obsługuje błędy separatorów."""
    data = {}
    try:
        # 1. Mapa Karier (To ma PRZECINKI - domyślnie)
        data["jobs"] = pd.read_csv("mapa_karier_COMPLETED.csv")
        
        # 2. Macierze Treści (To ma ŚREDNIKI - więc dodajemy sep=';')
        # - widać średniki
        data["personality"] = pd.read_csv("db_personality.csv", sep=';')
        data["career"] = pd.read_csv("db_career.csv", sep=';')
        data["communication"] = pd.read_csv("db_communication.csv", sep=';')
        data["ef"] = pd.read_csv("db_ef.csv", sep=';')
        data["motivation"] = pd.read_csv("db_motivation.csv", sep=';')
        
        return data
    except FileNotFoundError as e:
        st.error(f"❌ BŁĄD KRYTYCZNY: Nie znaleziono pliku: {e.filename}. Sprawdź GitHub.")
        return None
    except Exception as e:
        st.error(f"❌ BŁĄD DANYCH: {e}")
        return None

# Ładowanie danych przy starcie
DB = load_data()

# --- 3. ALGORYTMY LOGICZNE (ENGINE) ---

def auto_tag_jobs(df):
    """Algorytm NLP (Słownikowy) tagujący zawody w locie."""
    keywords = {
        "R": ["narzędzia", "maszyny", "naprawa", "montaż", "fizyczna", "sprzęt", "konstrukcje", "instalacje", "kierowca", "mechanik", "inżynier", "budowa", "teren", "ruch"],
        "I": ["analiza", "badania", "nauka", "rozwiązywanie", "logika", "teoria", "eksperyment", "dane", "programowanie", "biologia", "chemia", "fizyka", "matematyka", "diagnoza"],
        "A": ["sztuka", "projektowanie", "grafika", "muzyka", "pisanie", "kreatywność", "tworzenie", "wyobraźnia", "media", "kultura", "design", "styl", "artysta"],
        "S": ["ludzie", "pomoc", "nauczanie", "opieka", "współpraca", "terapia", "doradztwo", "szkolenia", "dzieci", "pacjent", "klient", "zespół", "rozmowa"],
        "E": ["zarządzanie", "sprzedaż", "biznes", "lider", "negocjacje", "marketing", "przedsiębiorczość", "decydowanie", "ryzyko", "kierowanie", "prezes", "strategia"],
        "C": ["biuro", "dane", "organizacja", "procedury", "finanse", "księgowość", "dokładność", "archiwizacja", "administracja", "porządek", "prawo", "regulamin"]
    }
    
    tagged_rows = []
    
    # Zabezpieczenie przed pustym DataFrame
    if df is None: return pd.DataFrame()

    for _, row in df.iterrows():
        text = str(row.get('Krotki_Opis', '')) + " " + str(row.get('Pelny_Opis', '')) + " " + str(row.get('Wymagania', ''))
        text = text.lower()
        
        scores = {code: 0 for code in keywords}
        for code, words in keywords.items():
            for word in words:
                if word in text:
                    scores[code] += 1
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_scores[0][0]
        secondary = sorted_scores[1][0]
        
        stress_words = ["stres", "presja", "terminy", "odpowiedzialność", "ryzyko", "konflikt", "awarie", "wypadki", "dyżur", "napięcie"]
        stress_level = sum(1 for w in stress_words if w in text)
        is_high_stress = stress_level >= 2
        
        tagged_rows.append({
            "Nazwa": row['Nazwa_Zawodu'],
            "Link": row['Link'],
            "Opis": row['Krotki_Opis'],
            "Wymagania": row['Wymagania'],
            "Kod_RIASEC": primary + secondary,
            "High_Stress": is_high_stress
        })
        
    return pd.DataFrame(tagged_rows)

if DB is not None and "jobs" in DB:
    DF_JOBS_TAGGED = auto_tag_jobs(DB["jobs"])
else:
    DF_JOBS_TAGGED = pd.DataFrame()

# Funkcje pomocnicze
def calc_big5_lvl(score):
    if score >= 65: return "High"
    if score <= 35: return "Low"
    return "Mid"

def calc_riasec_code(scores_dict):
    sorted_scores = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores[0][0] + sorted_scores[1][0]

def calc_social_style(assertiveness, responsiveness):
    if assertiveness > 50: return "D" if responsiveness < 50 else "I"
    else: return "C" if responsiveness < 50 else "S"

# --- 4. INTERFEJS UŻYTKOWNIKA (INPUT) ---

st.title("🧬 Who Am I: Generator Tożsamości i Kariery")
st.markdown("Wypełnij parametry testów (symulacja), aby wygenerować swój **Blueprint** i **Scenariusze Kariery**.")

with st.sidebar:
    st.header("🎛️ Panel Sterowania")
    
    st.subheader("1. Osobowość (Big 5)")
    neuro = st.slider("Neurotyczność (N)", 0, 100, 70)
    extra = st.slider("Ekstrawersja (E)", 0, 100, 45)
    openness = st.slider("Otwartość (O)", 0, 100, 60)
    agree = st.slider("Ugodowość (A)", 0, 100, 50)
    consc = st.slider("Sumienność (C)", 0, 100, 25)
    
    st.subheader("2. Zainteresowania (RIASEC)")
    r_val = st.number_input("R (Realistic)", 0, 100, 10)
    i_val = st.number_input("I (Investigative)", 0, 100, 20)
    a_val = st.number_input("A (Artistic)", 0, 100, 45)
    s_val = st.number_input("S (Social)", 0, 100, 15)
    e_val = st.number_input("E (Enterprising)", 0, 100, 35)
    c_val = st.number_input("C (Conventional)", 0, 100, 5)
    
    st.subheader("3. Styl Komunikacji")
    comm_ask_tell = st.slider("Ask (0) <-> Tell (100)", 0, 100, 80)
    comm_task_ppl = st.slider("Task (0) <-> People (100)", 0, 100, 30)
    
    st.subheader("4. Funkcje Wykonawcze")
    ef_focus = st.slider("EF: Skupienie (Focus)", 0, 100, 40)
    
    st.subheader("5. Motywacja")
    mot_comp = st.slider("Poczucie Kompetencji", 0, 100, 30)

    run_btn = st.button("🚀 GENERUJ PROFIL", type="primary")

# --- 5. LOGIKA WYKONAWCZA (OUTPUT) ---

if run_btn and DB is not None:
    # --- A. PRZELICZENIA ---
    user_riasec_scores = {"R": r_val, "I": i_val, "A": a_val, "S": s_val, "E": e_val, "C": c_val}
    user_code = calc_riasec_code(user_riasec_scores)
    user_style = calc_social_style(comm_ask_tell, comm_task_ppl)
    n_lvl = calc_big5_lvl(neuro)
    c_lvl = calc_big5_lvl(consc)
    
    # --- B. WIZUALIZACJA: KARTA POSTACI ---
    st.divider()
    st.header(f"Twoja Karta Postaci: {user_code}")
    
    col1, col2, col3 = st.columns(3)
    
    # 1. Moduł KARIERA
    try:
        # - Kluczem jest 'Kod Hybrydy'
        row_career = DB["career"][DB["career"]['Kod Hybrydy'] == user_code].iloc[0]
        col1.markdown(f"### 🛡️ Klasa: {row_career['Archetyp (Klasa)']}")
        col1.info(f"**Supermoc:** {row_career['Twoja Supermoc (Skillset)']}")
        col1.markdown(f"*„{row_career['Motto (Vibe)']}”*")
    except Exception:
        col1.error(f"Brak danych dla kodu {user_code}")

    # 2. Moduł OSOBOWOŚĆ
    col2.markdown("### 🧠 System Operacyjny")
    # - Logika Spikes Only
    if n_lvl == "High": col2.warning("**Wysoka Neurotyczność:** Symulator Katastrof.")
    elif n_lvl == "Low": col2.success("**Niska Neurotyczność:** Iceman.")
    
    if c_lvl == "High": col2.success("**Wysoka Sumienność:** Strateg.")
    elif c_lvl == "Low": col2.warning("**Niska Sumienność:** Improwizator.")

    # 3. Moduł KOMUNIKACJA
    try:
        # - Kluczem jest 'Kod Stylu'
        row_comm = DB["communication"][DB["communication"]['Kod Stylu'] == user_style].iloc[0]
        col3.markdown(f"### 💬 Styl: {row_comm['Archetyp (Klasa)']}")
        col3.error(f"**Rage Mode:** {str(row_comm['ULTIMATE (Stres / Rage Mode)']).split('.')[0]}")
    except Exception:
        col3.error("Błąd danych komunikacji")

    # --- C. SILNIK REKOMENDACJI ---
    st.divider()
    st.header("🎯 Dopasowane Ścieżki Kariery")
    
    if DF_JOBS_TAGGED.empty:
        st.warning("Baza zawodów jest pusta lub nie załadowała się poprawnie.")
    else:
        # Matching Logic
        match_perfect = DF_JOBS_TAGGED[DF_JOBS_TAGGED['Kod_RIASEC'] == user_code]
        match_reverse = DF_JOBS_TAGGED[DF_JOBS_TAGGED['Kod_RIASEC'] == user_code[::-1]]
        match_partial = DF_JOBS_TAGGED[DF_JOBS_TAGGED['Kod_RIASEC'].str.startswith(user_code[0])]
        
        recommendations = pd.concat([match_perfect, match_reverse, match_partial]).drop_duplicates().head(3)
        
        if recommendations.empty:
            st.warning("Brak idealnych dopasowań.")
        else:
            for i, (idx, job) in enumerate(recommendations.iterrows()):
                with st.expander(f"OPCJA #{i+1}: {job['Nazwa']}", expanded=True):
                    st.markdown(f"**Kod:** `{job['Kod_RIASEC']}` | **Opis:** {job['Opis']}")
                    st.markdown(f"[➡️ Zobacz profil]({job['Link']})")
                    
                    # Analiza Ryzyka
                    if job['High_Stress'] and n_lvl == "High":
                        st.error("⚠️ **Ryzyko Wypalenia:** Wysoki stres vs Wysoka Neurotyczność.")
                    elif str(job['Wymagania']).lower().find("organizacja") != -1 and c_lvl == "Low":
                         st.warning("⚠️ **Wymagana Dyscyplina:** Uwaga na niską sumienność.")
                    else:
                        st.success("✅ Profil Bezpieczny.")

elif DB is None:
    st.warning("⚠️ Problem z ładowaniem bazy danych. Sprawdź pliki CSV w repozytorium.")
else:
    st.info("👈 Ustaw suwaki i kliknij **GENERUJ PROFIL**.")