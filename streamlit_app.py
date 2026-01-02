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
    """Ładuje pliki CSV z repozytorium i obsługuje błędy."""
    data = {}
    try:
        # 1. Mapa Karier (Surowe dane zawodów)
        data["jobs"] = pd.read_csv("mapa_karier_COMPLETED.csv")
        
        # 2. Macierze Treści (Logika "Who Am I")
        data["personality"] = pd.read_csv("db_personality.csv")
        data["career"] = pd.read_csv("db_career.csv")
        data["communication"] = pd.read_csv("db_communication.csv")
        data["ef"] = pd.read_csv("db_ef.csv")
        data["motivation"] = pd.read_csv("db_motivation.csv")
        
        return data
    except FileNotFoundError as e:
        st.error(f"❌ BŁĄD KRYTYCZNY: Nie znaleziono pliku: {e.filename}. Upewnij się, że plik jest w repozytorium GitHub.")
        return None

# Ładowanie danych przy starcie
DB = load_data()

# --- 3. ALGORYTMY LOGICZNE (ENGINE) ---

def auto_tag_jobs(df):
    """
    Algorytm NLP (Słownikowy): Skanuje opisy zawodów i przypisuje im kody RIASEC oraz poziom stresu.
    Działa w locie, bo mapa_karier_COMPLETED.csv nie ma tych kolumn.
    """
    # Słowa kluczowe dla kodów Hollanda
    keywords = {
        "R": ["narzędzia", "maszyny", "naprawa", "montaż", "fizyczna", "sprzęt", "konstrukcje", "instalacje", "kierowca", "mechanik", "inżynier", "budowa", "teren", "ruch"],
        "I": ["analiza", "badania", "nauka", "rozwiązywanie", "logika", "teoria", "eksperyment", "dane", "programowanie", "biologia", "chemia", "fizyka", "matematyka", "diagnoza"],
        "A": ["sztuka", "projektowanie", "grafika", "muzyka", "pisanie", "kreatywność", "tworzenie", "wyobraźnia", "media", "kultura", "design", "styl", "artysta"],
        "S": ["ludzie", "pomoc", "nauczanie", "opieka", "współpraca", "terapia", "doradztwo", "szkolenia", "dzieci", "pacjent", "klient", "zespół", "rozmowa"],
        "E": ["zarządzanie", "sprzedaż", "biznes", "lider", "negocjacje", "marketing", "przedsiębiorczość", "decydowanie", "ryzyko", "kierowanie", "prezes", "strategia"],
        "C": ["biuro", "dane", "organizacja", "procedury", "finanse", "księgowość", "dokładność", "archiwizacja", "administracja", "porządek", "prawo", "regulamin"]
    }
    
    tagged_rows = []
    
    for _, row in df.iterrows():
        # Łączymy pola tekstowe do analizy
        text = str(row.get('Krotki_Opis', '')) + " " + str(row.get('Pelny_Opis', '')) + " " + str(row.get('Wymagania', ''))
        text = text.lower()
        
        # Zliczanie punktów dla każdej litery RIASEC
        scores = {code: 0 for code in keywords}
        for code, words in keywords.items():
            for word in words:
                if word in text:
                    scores[code] += 1
        
        # Wyznaczanie kodu (Top 2)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_scores[0][0]
        secondary = sorted_scores[1][0]
        
        # Wykrywanie stresu
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

# Generowanie otagowanej bazy zawodów (tylko raz)
if DB is not None:
    DF_JOBS_TAGGED = auto_tag_jobs(DB["jobs"])

# Funkcje pomocnicze z Blueprintu
def calc_big5_lvl(score):
    if score >= 65: return "High"
    if score <= 35: return "Low"
    return "Mid"

def calc_riasec_code(scores_dict):
    sorted_scores = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores[0][0] + sorted_scores[1][0]

def calc_social_style(assertiveness, responsiveness):
    # Model Merrill-Reid
    if assertiveness > 50: # Tell
        return "D" if responsiveness < 50 else "I" # Task vs People
    else: # Ask
        return "C" if responsiveness < 50 else "S"

# --- 4. INTERFEJS UŻYTKOWNIKA (INPUT) ---

st.title("🧬 Who Am I: Generator Tożsamości i Kariery")
st.markdown("Wypełnij parametry testów (symulacja), aby wygenerować swój **Blueprint** i **Scenariusze Kariery**.")

with st.sidebar:
    st.header("🎛️ Panel Sterowania")
    
    st.subheader("1. Osobowość (Big 5)")
    neuro = st.slider("Neurotyczność (N)", 0, 100, 70, help="Skłonność do stresu i lęku")
    extra = st.slider("Ekstrawersja (E)", 0, 100, 45)
    openness = st.slider("Otwartość (O)", 0, 100, 60)
    agree = st.slider("Ugodowość (A)", 0, 100, 50)
    consc = st.slider("Sumienność (C)", 0, 100, 25, help="Dyscyplina i porządek")
    
    st.subheader("2. Zainteresowania (RIASEC)")
    r_val = st.number_input("R (Realistic)", 0, 100, 10)
    i_val = st.number_input("I (Investigative)", 0, 100, 20)
    a_val = st.number_input("A (Artistic)", 0, 100, 45)
    s_val = st.number_input("S (Social)", 0, 100, 15)
    e_val = st.number_input("E (Enterprising)", 0, 100, 35)
    c_val = st.number_input("C (Conventional)", 0, 100, 5)
    
    st.subheader("3. Styl Komunikacji")
    comm_ask_tell = st.slider("Ask (0) <-> Tell (100)", 0, 100, 80, help="Asertywność")
    comm_task_ppl = st.slider("Task (0) <-> People (100)", 0, 100, 30, help="Relacyjność")
    
    st.subheader("4. Funkcje Wykonawcze")
    ef_focus = st.slider("EF: Skupienie (Focus)", 0, 100, 40)
    ef_action = st.slider("EF: Działanie (Action)", 0, 100, 80)
    
    st.subheader("5. Motywacja")
    mot_comp = st.slider("Poczucie Kompetencji", 0, 100, 30, help="Czy czujesz się skuteczny?")

    run_btn = st.button("🚀 GENERUJ PROFIL", type="primary")

# --- 5. LOGIKA WYKONAWCZA (OUTPUT) ---

if run_btn and DB is not None:
    # --- A. PRZELICZENIA ---
    # Kod użytkownika RIASEC
    user_riasec_scores = {"R": r_val, "I": i_val, "A": a_val, "S": s_val, "E": e_val, "C": c_val}
    user_code = calc_riasec_code(user_riasec_scores)
    
    # Styl komunikacji
    user_style = calc_social_style(comm_ask_tell, comm_task_ppl)
    
    # Poziomy Big5 (tylko kluczowe dla logiki kariery)
    n_lvl = calc_big5_lvl(neuro)
    c_lvl = calc_big5_lvl(consc)
    
    # --- B. WIZUALIZACJA: KARTA POSTACI ---
    st.divider()
    st.header(f"Twoja Karta Postaci: {user_code}")
    
    col1, col2, col3 = st.columns(3)
    
    # 1. Moduł KARIERA (Tytuł + Opis)
    try:
        row_career = DB["career"][DB["career"]['Kod Hybrydy'] == user_code].iloc[0]
        col1.markdown(f"### 🛡️ Klasa: {row_career['Archetyp (Klasa)']}")
        col1.info(f"**Supermoc:** {row_career['Twoja Supermoc (Skillset)']}")
        col1.markdown(f"*„{row_career['Motto (Vibe)']}”*")
    except IndexError:
        col1.error(f"Nie znaleziono opisu dla kodu {user_code}")

    # 2. Moduł OSOBOWOŚĆ (Tylko Spikes)
    col2.markdown("### 🧠 System Operacyjny")
    if n_lvl == "High":
        col2.warning("**Wysoka Neurotyczność:** Symulator Katastrof. Widzisz ryzyka, których inni nie widzą.")
    elif n_lvl == "Low":
        col2.success("**Niska Neurotyczność:** Iceman. Zachowujesz zimną krew.")
    
    if c_lvl == "High":
        col2.success("**Wysoka Sumienność:** Strateg. Planujesz wszystko z wyprzedzeniem.")
    elif c_lvl == "Low":
        col2.warning("**Niska Sumienność:** Improwizator. Działasz pod wpływem impulsu (i deadline'u).")

    # 3. Moduł KOMUNIKACJA
    try:
        row_comm = DB["communication"][DB["communication"]['Kod Stylu'] == user_style].iloc[0]
        col3.markdown(f"### 💬 Styl: {row_comm['Archetyp (Klasa)']}")
        col3.error(f"**Rage Mode:** {str(row_comm['ULTIMATE (Stres / Rage Mode)']).split('.')[0]}")
        col3.caption(f"Kod: {user_style} (Merrill-Reid)")
    except IndexError:
        col3.error("Błąd danych komunikacji")

    # --- C. SILNIK REKOMENDACJI KARIERY (MATCHING ENGINE) ---
    st.divider()
    st.header("🎯 Dopasowane Ścieżki Kariery")
    st.markdown(f"Algorytm przeszukał **{len(DF_JOBS_TAGGED)} zawodów** pod kątem zgodności z profilem **{user_code}**.")
    
    # 1. Filtrowanie (Logika Matchingu)
    # Match Idealny (np. AE -> AE)
    match_perfect = DF_JOBS_TAGGED[DF_JOBS_TAGGED['Kod_RIASEC'] == user_code]
    # Match Odwrócony (np. AE -> EA)
    match_reverse = DF_JOBS_TAGGED[DF_JOBS_TAGGED['Kod_RIASEC'] == user_code[::-1]]
    # Match Częściowy (Zgodna pierwsza litera)
    match_partial = DF_JOBS_TAGGED[DF_JOBS_TAGGED['Kod_RIASEC'].str.startswith(user_code[0])]
    
    # Łączenie wyników (priorytetyzacja)
    recommendations = pd.concat([match_perfect, match_reverse, match_partial]).drop_duplicates().head(3)
    
    if recommendations.empty:
        st.warning("Brak idealnych dopasowań. Spróbuj zmienić parametry RIASEC.")
    else:
        # Pętla po wynikach
        for i, (idx, job) in enumerate(recommendations.iterrows()):
            with st.container():
                # Nagłówek kafelka
                st.subheader(f"#{i+1} {job['Nazwa']}")
                
                c_desc, c_analysis = st.columns([2, 1])
                
                with c_desc:
                    st.markdown(f"**Kod Zawodu:** `{job['Kod_RIASEC']}`")
                    st.markdown(f"{job['Opis']}")
                    # Link do mapy karier
                    st.markdown(f"[➡️ Zobacz pełny profil na MapaKarier.org]({job['Link']})")
                    
                    # Dlaczego to pasuje?
                    st.success(f"**Dlaczego Ty?** Ten zawód wykorzystuje Twoją dominującą cechę **{user_code[0]}** (zgodność z archetypem {row_career['Archetyp (Klasa)']}).")

                with c_analysis:
                    st.markdown("**📊 Analiza Ryzyka**")
                    risk_found = False
                    
                    # Logika Ryzyka (BETA)
                    # 1. Neurotyczność vs Stres
                    if job['High_Stress'] and n_lvl == "High":
                        st.error("⚠️ **Ryzyko Wypalenia:** Zawód o wysokim stresie przy Twojej wysokiej wrażliwości wymaga solidnych technik relaksacji.")
                        risk_found = True
                    
                    # 2. Sumienność vs Wymagania
                    reqs = str(job['Wymagania']).lower()
                    if ("organizacja" in reqs or "terminowość" in reqs) and c_lvl == "Low":
                        st.warning("⚠️ **Wymagana Dyscyplina:** Ten zawód wymaga systematyczności, która może być dla Ciebie wyzwaniem.")
                        risk_found = True
                        
                    # 3. EF (Focus)
                    if ef_focus < 40 and ("analiza" in reqs or "skupienie" in reqs):
                         st.warning("⚠️ **Głęboka Praca:** Zawód wymaga długiego skupienia uwagi (EF Focus).")
                         risk_found = True

                    if not risk_found:
                        st.info("✅ **Profil Bezpieczny:** Brak krytycznych przeciwwskazań osobowościowych.")

                st.divider()

elif DB is None:
    st.warning("Oczekiwanie na dane...")
else:
    st.info("👈 Ustaw suwaki w panelu bocznym i kliknij **GENERUJ PROFIL**, aby uruchomić symulację.")