import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Who Am I: Test Rzeczywisty",
    page_icon="🧬",
    layout="wide"
)

# --- CSS ---
st.markdown("""
<style>
    .question-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 5px solid #2e86c1; }
    .header-section { font-size: 24px; font-weight: bold; margin-top: 30px; margin-bottom: 10px; color: #2c3e50; }
    .stRadio > label { display: none; } /* Ukrywa etykietę radio buttona dla czystości */
</style>
""", unsafe_allow_html=True)

# --- 2. BAZA PYTAŃ (Unikalne ID) ---
QUESTIONS = {
    "BIG5": [
        {"id": "BIG5_N1", "txt": "Często się denerwuję lub stresuję.", "domain": "neuro", "rev": False},
        {"id": "BIG5_N2", "txt": "Rzadko czuję się przygnębiony.", "domain": "neuro", "rev": True},
        {"id": "BIG5_E1", "txt": "Lubię być w centrum uwagi.", "domain": "extra", "rev": False},
        {"id": "BIG5_E2", "txt": "Wolę spędzać czas w samotności.", "domain": "extra", "rev": True},
        {"id": "BIG5_O1", "txt": "Mam bogatą wyobraźnię i lubię abstrakcyjne idee.", "domain": "open", "rev": False},
        {"id": "BIG5_A1", "txt": "Uważam, że większość ludzi ma dobre intencje.", "domain": "agree", "rev": False},
        {"id": "BIG5_C1", "txt": "Lubię porządek i zawsze kończę to, co zacząłem.", "domain": "consc", "rev": False},
        {"id": "BIG5_C2", "txt": "Często zapominam odłożyć rzeczy na miejsce.", "domain": "consc", "rev": True},
    ],
    "RIASEC": [
        {"id": "RIA_R1", "txt": "Lubię naprawiać sprzęty, majsterkować lub pracować narzędziami.", "cat": "R"},
        {"id": "RIA_R2", "txt": "Wolałbym pracować fizycznie na zewnątrz niż w biurze.", "cat": "R"},
        {"id": "RIA_I1", "txt": "Lubię rozwiązywać zagadki logiczne i analizować dane.", "cat": "I"},
        {"id": "RIA_I2", "txt": "Ciekawi mnie, jak działają zjawiska przyrodnicze (fizyka, biologia).", "cat": "I"},
        {"id": "RIA_A1", "txt": "Jestem osobą kreatywną (piszę, maluję, gram, projektuję).", "cat": "A"},
        {"id": "RIA_A2", "txt": "Cenię sobie swobodę ekspresji i nie lubię sztywnych reguł.", "cat": "A"},
        {"id": "RIA_S1", "txt": "Lubię pomagać innym, uczyć ich lub doradzać.", "cat": "S"},
        {"id": "RIA_S2", "txt": "Jestem dobry w rozumieniu uczuć innych ludzi.", "cat": "S"},
        {"id": "RIA_E1", "txt": "Lubię przewodzić grupie i przekonywać innych do swoich racji.", "cat": "E"},
        {"id": "RIA_E2", "txt": "Interesuje mnie biznes, sprzedaż i zarabianie pieniędzy.", "cat": "E"},
        {"id": "RIA_C1", "txt": "Lubię jasne procedury, tabelki i porządek w dokumentach.", "cat": "C"},
        {"id": "RIA_C2", "txt": "Jestem osobą bardzo dokładną i skrupulatną.", "cat": "C"},
    ],
    "COMM": [
        {"id": "COM_X1", "txt": "W rozmowie częściej słucham i pytam, niż mówię i oznajmiam.", "axis": "ask_tell", "dir": -1}, # Ask
        {"id": "COM_X2", "txt": "Kiedy czegoś chcę, mówię o tym wprost i stanowczo.", "axis": "ask_tell", "dir": 1},   # Tell
        {"id": "COM_Y1", "txt": "W pracy ważniejsze są dla mnie relacje z ludźmi niż odhaczenie zadań.", "axis": "task_ppl", "dir": 1}, # People
        {"id": "COM_Y2", "txt": "Wolę trzymać się faktów i logiki, emocje odkładam na bok.", "axis": "task_ppl", "dir": -1} # Task
    ],
    "EF": [
        {"id": "EF_1", "txt": "Potrafię skupić się na nudnym zadaniu przez długi czas.", "cluster": "focus"},
        {"id": "EF_2", "txt": "Zanim coś powiem lub zrobię, zastanawiam się nad konsekwencjami.", "cluster": "action"}
    ]
}

# --- 3. WARSTWA DANYCH (DATA LAYER) ---
@st.cache_data
def load_data():
    try:
        data = {}
        # 1. Mapa Karier
        data["jobs"] = pd.read_csv("mapa_karier_COMPLETED.csv")
        
        # 2. Macierze Treści (FIX: Czyścimy klucze przy ładowaniu)
        # Dzięki temu "RI (Maker)" zamienia się na "RI" i pasuje do algorytmu.
        
        career_df = pd.read_csv("db_career.csv", sep=';')
        # [FIX] Bierzemy tylko pierwszy człon kodu (przed spacją)
        career_df['Kod Hybrydy'] = career_df['Kod Hybrydy'].astype(str).apply(lambda x: x.split(' ')[0])
        data["career"] = career_df

        comm_df = pd.read_csv("db_communication.csv", sep=';')
        # [FIX] To samo dla komunikacji (D (Driver) -> D)
        comm_df['Kod Stylu'] = comm_df['Kod Stylu'].astype(str).apply(lambda x: x.split(' ')[0])
        data["communication"] = comm_df
        
        data["personality"] = pd.read_csv("db_personality.csv", sep=';')
        data["ef"] = pd.read_csv("db_ef.csv", sep=';')
        data["motivation"] = pd.read_csv("db_motivation.csv", sep=';')
        
        return data
    except Exception as e:
        st.error(f"Błąd ładowania danych: {e}")
        return None

DB = load_data()

# --- 4. FUNKCJE POMOCNICZE ---

def render_likert(question_id, label):
    st.markdown(f"<div class='question-card'><b>{label}</b></div>", unsafe_allow_html=True)
    val = st.radio(
        f"q_{question_id}", 
        options=[1, 2, 3, 4, 5], 
        format_func=lambda x: {1: "Zdecydowanie NIE", 2: "Raczej NIE", 3: "Trudno powiedzieć", 4: "Raczej TAK", 5: "Zdecydowanie TAK"}[x],
        horizontal=True,
        key=question_id,
        label_visibility="collapsed"
    )
    return val

def calc_percentage(points, max_points):
    if max_points == 0: return 0
    return int((points / max_points) * 100)

def auto_tag_jobs(df):
    keywords = {
        "R": ["narzędzia", "maszyny", "naprawa", "montaż", "fizyczna", "sprzęt", "konstrukcje", "instalacje", "kierowca", "mechanik", "inżynier", "budowa"],
        "I": ["analiza", "badania", "nauka", "rozwiązywanie", "logika", "teoria", "eksperyment", "dane", "programowanie", "biologia", "chemia", "fizyka"],
        "A": ["sztuka", "projektowanie", "grafika", "muzyka", "pisanie", "kreatywność", "tworzenie", "wyobraźnia", "media", "kultura", "design"],
        "S": ["ludzie", "pomoc", "nauczanie", "opieka", "współpraca", "terapia", "doradztwo", "szkolenia", "dzieci", "pacjent", "klient"],
        "E": ["zarządzanie", "sprzedaż", "biznes", "lider", "negocjacje", "marketing", "przedsiębiorczość", "decydowanie", "ryzyko", "kierowanie"],
        "C": ["biuro", "dane", "organizacja", "procedury", "finanse", "księgowość", "dokładność", "archiwizacja", "administracja", "porządek"]
    }
    
    tagged_rows = []
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
        
        stress_words = ["stres", "presja", "terminy", "odpowiedzialność", "ryzyko", "konflikt", "awarie", "wypadki"]
        is_high_stress = any(w in text for w in stress_words)
        
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

# --- 5. INTERFEJS (FORMULARZ TESTU) ---

st.title("🧬 Who Am I: Official Assessment")
st.markdown("Odpowiedz szczerze. Nie ma dobrych i złych odpowiedzi.")

with st.form("test_form"):
    
    # SEKCJA 1: OSOBOWOŚĆ
    st.markdown("<div class='header-section'>1. Jaki jesteś na co dzień? (Osobowość)</div>", unsafe_allow_html=True)
    scores_big5 = {"neuro": [], "extra": [], "open": [], "agree": [], "consc": []}
    
    for q in QUESTIONS["BIG5"]:
        ans = render_likert(q['id'], q['txt'])
        if q['rev']: ans = 6 - ans 
        scores_big5[q['domain']].append(ans)

    # SEKCJA 2: ZAINTERESOWANIA ZAWODOWE
    st.markdown("<div class='header-section'>2. Co lubisz robić? (Kariera)</div>", unsafe_allow_html=True)
    scores_riasec = {"R": [], "I": [], "A": [], "S": [], "E": [], "C": []}
    
    for q in QUESTIONS["RIASEC"]:
        ans = render_likert(q['id'], q['txt'])
        scores_riasec[q['cat']].append(ans)
        
    # SEKCJA 3: STYL KOMUNIKACJI
    st.markdown("<div class='header-section'>3. Jak dogadujesz się z ludźmi?</div>", unsafe_allow_html=True)
    val_ask_tell = 50 
    val_task_ppl = 50 
    
    for q in QUESTIONS["COMM"]:
        ans = render_likert(q['id'], q['txt'])
        shift = (ans - 3) * 10 * q['dir'] 
        if q['axis'] == 'ask_tell': val_ask_tell += shift
        else: val_task_ppl += shift

    # SEKCJA 4: FUNKCJE WYKONAWCZE
    st.markdown("<div class='header-section'>4. Jak działa Twój mózg?</div>", unsafe_allow_html=True)
    scores_ef = {"focus": [], "action": []}
    for q in QUESTIONS["EF"]:
        ans = render_likert(q['id'], q['txt'])
        scores_ef[q['cluster']].append(ans)

    submit = st.form_submit_button("🏁 ZAKOŃCZ TEST I POKAŻ WYNIK", type="primary")

# --- 6. OBLICZANIE WYNIKÓW I RAPORT ---

if submit and DB is not None:
    
    # 1. PRZELICZANIE BIG5
    res_neuro = calc_percentage(sum(scores_big5['neuro']), len(scores_big5['neuro'])*5)
    res_consc = calc_percentage(sum(scores_big5['consc']), len(scores_big5['consc'])*5)
    
    # 2. PRZELICZANIE RIASEC
    final_riasec = {k: sum(v) for k, v in scores_riasec.items()}
    sorted_riasec = sorted(final_riasec.items(), key=lambda x: x[1], reverse=True)
    user_code = sorted_riasec[0][0] + sorted_riasec[1][0]
    
    # 3. STYLE
    res_ask_tell = max(0, min(100, val_ask_tell))
    res_task_ppl = max(0, min(100, val_task_ppl))
    
    def get_style_code(at, tp):
        if at > 50: return "D" if tp < 50 else "I"
        else: return "C" if tp < 50 else "S"
    
    user_style = get_style_code(res_ask_tell, res_task_ppl)

    # 4. EF
    ef_focus_score = sum(scores_ef['focus']) if scores_ef['focus'] else 0
    res_ef_focus = calc_percentage(ef_focus_score, len(scores_ef['focus'])*5) if scores_ef['focus'] else 0

    # --- GENEROWANIE RAPORTU ---
    
    st.divider()
    st.title(f"Twój Wynik: {user_code}")
    
    # Moduł Kariera
    try:
        # [FIX] Teraz zadziała, bo w load_data obcięliśmy (Maker+Hacker)
        row_career = DB["career"][DB["career"]['Kod Hybrydy'] == user_code].iloc[0]
        st.success(f"**Archetyp Kariery:** {row_career['Archetyp (Klasa)']}")
        st.markdown(f"_{row_career['Motto (Vibe)']}_")
    except IndexError:
        st.error(f"Nie znaleziono opisu dla kodu: {user_code}. Sprawdź plik db_career.csv.")
        
    # Moduł Osobowości
    st.subheader("Twoja Mapa Mentalna")
    c1, c2 = st.columns(2)
    
    if res_neuro >= 65: 
        c1.warning(f"Neurotyczność: {res_neuro}% (HIGH) - Uważaj na stres.")
    elif res_neuro <= 35:
        c1.info(f"Neurotyczność: {res_neuro}% (LOW) - Oaza spokoju.")
    else:
        c1.write(f"Neurotyczność: {res_neuro}% (MID) - W normie.")
        
    if res_consc >= 65:
        c2.success(f"Sumienność: {res_consc}% (HIGH) - Zorganizowany.")
    elif res_consc <= 35:
        c2.warning(f"Sumienność: {res_consc}% (LOW) - Spontaniczny.")
        
    # --- MATCHING ZAWODÓW (NOWA LOGIKA: SHOW ALL) ---
    st.divider()
    
    if DF_JOBS_TAGGED.empty:
        st.warning("Baza zawodów jest pusta.")
    else:
        # 1. Matching
        match_perfect = DF_JOBS_TAGGED[DF_JOBS_TAGGED['Kod_RIASEC'] == user_code]
        match_reverse = DF_JOBS_TAGGED[DF_JOBS_TAGGED['Kod_RIASEC'] == user_code[::-1]]
        match_partial = DF_JOBS_TAGGED[DF_JOBS_TAGGED['Kod_RIASEC'].str.startswith(user_code[0])]
        
        # 2. Łączenie bez limitu .head()
        recommendations = pd.concat([match_perfect, match_reverse, match_partial]).drop_duplicates()
        
        # 3. Wyświetlanie licznika
        count = len(recommendations)
        st.subheader(f"🎯 Rekomendowane Ścieżki: Znaleziono {count}")
        
        if recommendations.empty:
            st.warning("Brak dopasowań dla Twojego profilu.")
        else:
            # Pętla po wszystkich wynikach
            for i, (idx, job) in enumerate(recommendations.iterrows()):
                # Oznaczenie typu dopasowania (Dla jasności użytkownika)
                match_type = "IDEALNE" if job['Kod_RIASEC'] == user_code else ("DOBRE" if job['Kod_RIASEC'] == user_code[::-1] else "CZĘŚCIOWE")
                match_color = "green" if match_type == "IDEALNE" else ("orange" if match_type == "DOBRE" else "grey")
                
                with st.expander(f"#{i+1}: {job['Nazwa']} (:{match_color}[{match_type}])", expanded=(i<3)):
                    st.markdown(f"**Kod:** `{job['Kod_RIASEC']}` | **Opis:** {job['Opis']}")
                    st.markdown(f"[➡️ Zobacz profil na MapaKarier.org]({job['Link']})")
                    
                    risks = []
                    if job['High_Stress'] and res_neuro >= 65:
                        risks.append("⚠️ **Ryzyko Wypalenia:** Zawód o wysokim stresie przy Twojej wrażliwości.")
                    
                    reqs = str(job['Wymagania']).lower()
                    if ("organizacja" in reqs or "terminowość" in reqs) and res_consc <= 35:
                         risks.append("⚠️ **Wymagana Dyscyplina:** Ten zawód wymaga systematyczności.")
                    
                    if risks:
                        for r in risks: st.error(r)
                    else:
                        st.success("✅ Profil Bezpieczny (Brak czerwonych flag).")

elif submit and DB is None:
    st.error("Błąd krytyczny: Nie załadowano bazy danych.")