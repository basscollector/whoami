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

# --- 2. BAZA PYTAŃ (HARDCODED STARTER PACK) ---
# W wersji produkcyjnej przenieś to do db_questions.csv
QUESTIONS = {
    "BIG5": [
        {"id": "N1", "txt": "Często się denerwuję lub stresuję.", "domain": "neuro", "rev": False},
        {"id": "N2", "txt": "Rzadko czuję się przygnębiony.", "domain": "neuro", "rev": True},
        {"id": "E1", "txt": "Lubię być w centrum uwagi.", "domain": "extra", "rev": False},
        {"id": "E2", "txt": "Wolę spędzać czas w samotności.", "domain": "extra", "rev": True},
        {"id": "O1", "txt": "Mam bogatą wyobraźnię i lubię abstrakcyjne idee.", "domain": "open", "rev": False},
        {"id": "A1", "txt": "Uważam, że większość ludzi ma dobre intencje.", "domain": "agree", "rev": False},
        {"id": "C1", "txt": "Lubię porządek i zawsze kończę to, co zacząłem.", "domain": "consc", "rev": False},
        {"id": "C2", "txt": "Często zapominam odłożyć rzeczy na miejsce.", "domain": "consc", "rev": True},
    ],
    "RIASEC": [
        {"id": "R1", "txt": "Lubię naprawiać sprzęty, majsterkować lub pracować narzędziami.", "cat": "R"},
        {"id": "R2", "txt": "Wolałbym pracować fizycznie na zewnątrz niż w biurze.", "cat": "R"},
        {"id": "I1", "txt": "Lubię rozwiązywać zagadki logiczne i analizować dane.", "cat": "I"},
        {"id": "I2", "txt": "Ciekawi mnie, jak działają zjawiska przyrodnicze (fizyka, biologia).", "cat": "I"},
        {"id": "A1", "txt": "Jestem osobą kreatywną (piszę, maluję, gram, projektuję).", "cat": "A"},
        {"id": "A2", "txt": "Cenię sobie swobodę ekspresji i nie lubię sztywnych reguł.", "cat": "A"},
        {"id": "S1", "txt": "Lubię pomagać innym, uczyć ich lub doradzać.", "cat": "S"},
        {"id": "S2", "txt": "Jestem dobry w rozumieniu uczuć innych ludzi.", "cat": "S"},
        {"id": "E1", "txt": "Lubię przewodzić grupie i przekonywać innych do swoich racji.", "cat": "E"},
        {"id": "E2", "txt": "Interesuje mnie biznes, sprzedaż i zarabianie pieniędzy.", "cat": "E"},
        {"id": "C1", "txt": "Lubię jasne procedury, tabelki i porządek w dokumentach.", "cat": "C"},
        {"id": "C2", "txt": "Jestem osobą bardzo dokładną i skrupulatną.", "cat": "C"},
    ],
    "COMM": [
        {"id": "X1", "txt": "W rozmowie częściej słucham i pytam, niż mówię i oznajmiam.", "axis": "ask_tell", "dir": -1}, # Ask
        {"id": "X2", "txt": "Kiedy czegoś chcę, mówię o tym wprost i stanowczo.", "axis": "ask_tell", "dir": 1},   # Tell
        {"id": "Y1", "txt": "W pracy ważniejsze są dla mnie relacje z ludźmi niż odhaczenie zadań.", "axis": "task_ppl", "dir": 1}, # People
        {"id": "Y2", "txt": "Wolę trzymać się faktów i logiki, emocje odkładam na bok.", "axis": "task_ppl", "dir": -1} # Task
    ],
    "EF": [
        {"id": "EF1", "txt": "Potrafię skupić się na nudnym zadaniu przez długi czas.", "cluster": "focus"},
        {"id": "EF2", "txt": "Zanim coś powiem lub zrobię, zastanawiam się nad konsekwencjami.", "cluster": "action"}
    ]
}

# --- 3. WARSTWA DANYCH (DATA LAYER) ---
@st.cache_data
def load_data():
    try:
        data = {}
        # Upewnij się, że masz te pliki w repo (CSV oddzielane średnikami ; )
        data["jobs"] = pd.read_csv("mapa_karier_COMPLETED.csv") # Tu zazwyczaj przecinki
        data["personality"] = pd.read_csv("db_personality.csv", sep=';')
        data["career"] = pd.read_csv("db_career.csv", sep=';')
        data["communication"] = pd.read_csv("db_communication.csv", sep=';')
        data["ef"] = pd.read_csv("db_ef.csv", sep=';')
        data["motivation"] = pd.read_csv("db_motivation.csv", sep=';')
        return data
    except Exception as e:
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
    return int((points / max_points) * 100)

def auto_tag_jobs(df):
    # (Tu wklej tę samą funkcję auto_tag_jobs co w poprzedniej wersji - skracam dla czytelności)
    # ... Logika tagowania RIASEC ...
    # Jeśli nie masz jej pod ręką, użyj tej z poprzedniego promptu
    return df 

# --- 5. INTERFEJS (FORMULARZ TESTU) ---

st.title("🧬 Who Am I: Official Assessment")
st.markdown("Odpowiedz szczerze. Nie ma dobrych i złych odpowiedzi.")

with st.form("test_form"):
    
    # SEKCJA 1: OSOBOWOŚĆ
    st.markdown("<div class='header-section'>1. Jaki jesteś na co dzień? (Osobowość)</div>", unsafe_allow_html=True)
    scores_big5 = {"neuro": [], "extra": [], "open": [], "agree": [], "consc": []}
    
    for q in QUESTIONS["BIG5"]:
        ans = render_likert(q['id'], q['txt'])
        # Obsługa pytań odwróconych (Reversed)
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
    val_ask_tell = 50 # Start
    val_task_ppl = 50 # Start
    
    # Prosta logika wagowa dla osi
    for q in QUESTIONS["COMM"]:
        ans = render_likert(q['id'], q['txt'])
        # Skalowanie 1-5 na przesunięcie suwaka (-20 do +20 pkt)
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
    
    # 1. PRZELICZANIE BIG5 (Na skalę 0-100%)
    # Suma punktów / (Liczba pytań * 5)
    res_neuro = calc_percentage(sum(scores_big5['neuro']), len(scores_big5['neuro'])*5)
    res_consc = calc_percentage(sum(scores_big5['consc']), len(scores_big5['consc'])*5)
    
    # 2. PRZELICZANIE RIASEC (Punkty surowe)
    final_riasec = {k: sum(v) for k, v in scores_riasec.items()}
    # Sortowanie Top 2
    sorted_riasec = sorted(final_riasec.items(), key=lambda x: x[1], reverse=True)
    user_code = sorted_riasec[0][0] + sorted_riasec[1][0]
    
    # 3. STYLE
    # Clamp wartości 0-100
    res_ask_tell = max(0, min(100, val_ask_tell))
    res_task_ppl = max(0, min(100, val_task_ppl))
    
    def get_style_code(at, tp):
        if at > 50: return "D" if tp < 50 else "I"
        else: return "C" if tp < 50 else "S"
    
    user_style = get_style_code(res_ask_tell, res_task_ppl)

    # 4. EF
    res_ef_focus = calc_percentage(sum(scores_ef['focus']), len(scores_ef['focus'])*5)

    # --- GENEROWANIE RAPORTU ---
    
    st.divider()
    st.title(f"Twój Wynik: {user_code}")
    
    # Logika wyświetlania (taka sama jak w poprzednim, ale bierze obliczone zmienne)
    # Przykład Kariery
    try:
        row_career = DB["career"][DB["career"]['Kod Hybrydy'] == user_code].iloc[0]
        st.success(f"**Archetyp Kariery:** {row_career['Archetyp (Klasa)']}")
        st.markdown(f"_{row_career['Motto (Vibe)']}_")
    except:
        st.error("Błąd dopasowania kariery.")
        
    # Przykład Osobowości (Spikes)
    st.subheader("Twoja Mapa Mentalna")
    c1, c2 = st.columns(2)
    
    # Logika z Blueprint [cite: 21-23]
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
        
    # --- MATCHING ZAWODÓW (Krótki snippet) ---
    # Tu dodaj funkcję tagowania jeśli nie została zdefiniowana wyżej
    # ... matching logic ...
    st.info("Tutaj pojawiłyby się dopasowane zawody na bazie Twoich odpowiedzi (Logic from previous code).")

elif submit and DB is None:
    st.error("Błąd ładowania bazy danych. Sprawdź pliki CSV.")