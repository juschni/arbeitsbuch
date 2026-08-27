import streamlit as st
from google import genai
from google.genai import types
import pypdf

# PAGE CONFIG & STYLING
st.set_page_config(
    page_title="Rollen- & Kompetenzportfolio",
    page_icon="🛡️",
    layout="wide"
)

st.title("Rollen- & Kompetenzportfolio")
st.caption("20 Jahre HR · Blue Collar & Shift · KI & AI | Sicherheitsschuhe statt PowerPoint.")

st.markdown("""
---
**Anwendungszweck:** Dieses Werkzeug analysiert berufsbezogene Dokumente strikt nach der festgelegten Logik. 
Es extrahiert harte Fakten, dekodiert praxiserprobte Kompetenzen (inkl. verdeckter Fähigkeiten) und leitet tragfähige Rollen und Roadmaps ab.
""")

# API KEY HANDLING
api_key = st.sidebar.text_input("Gemini API Key eingeben:", type="password", help="Kostenlosen Key aus dem Google AI Studio eintragen.")

if not api_key:
    st.info("👈 Bitte trage deinen kostenlosen Gemini API Key in der Seitenleiste ein, um zu starten.")
    st.stop()

client = genai.Client(api_key=api_key)

# SYSTEM PROMPT
SYSTEM_PROMPT = """
Du bist das Analyse-System für Katja Jakobs 'Rollen- & Kompetenzportfolio'.
Deine Aufgabe ist es, aus den eingegebenen Dokumenten eine präzise, ehrliche und sachliche Strukturanalyse zu erstellen.

QUALITÄTSREGELN & PRINZIPIEN (STRIKT EINHALTEN):
1. Nichts erfinden. Wenn Daten fehlen, markiere sie explizit als [FEHLT/UNKLAR].
2. Trenne harten Fakten strikt von Interpretationen.
3. Unterstelle keine Kompetenzen rein aufgrund von Berufsbezeichnungen.
4. Keine generischen Buzzwords, kein Denglisch, kein Motivations-Sprech.
5. Keine Rechtsberatung behaupten. Arbeitsrechtliche Erfahrung ist rein als praktische HR-Erfahrung darzustellen.
6. Unterstelle KEINE Führungskompetenz oder Führungsambition.
7. Beschäftigte nicht als reine Datenobjekte behandeln.
8. Empfehlungen immer sachlich begründen und Unsicherheiten sichtbar machen.
9. Achte auf verdeckte Kompetenzen aus Schichtbetrieb, Produktion, gewerblicher Arbeit und belastenden Rahmenbedingungen.

ANALYSEKETTE & AUSGABESTRUKTUR:

Erzeuge die Ausgabe exakt in folgenden Abschnitten:

1. FAKTEN
- Festgestellte Daten: Arbeitgeber, Positionen, Zeiträume, Branchen, Ausbildungen, Arbeitsumgebungen (z.B. 24/7-Schicht, Produktion, Personaldienstleistung).
- Keine Interpretation, nur belegte Fakten.

2. ERFAHRUNG
- Dekodierung der tatsächlichen Praxis: Was hat die Person dort realistisch Tag für Tag getan?
- Kontextualisierung (z. B. Arbeit im Schichtsystem, Umgang mit Druck, Fertigungsnähe).

3. KOMPETENZMODELL
Unterteile explizit in:
- Fachkompetenz
- Methodenkompetenz
- Sozialkompetenz
- Praxiskompetenz (Was im Alltag tatsächlich beherrscht wird)
- Kontextkompetenz (Verständnis für spezifische Arbeitswelten)
- Verdeckte Kompetenzen (Fähigkeiten, die aus den Tätigkeiten hervorgehen, aber oft nicht im Lebenslauf stehen)

4. TRANSFERKOMPETENZ
- Welche der gefundenen Fähigkeiten lassen sich auf andere Branchen, Rollen oder digitale/prozessuale Kontexten übertragen?

5. ROLLEN-MATCHING (Drei Ebenen)
- Passt gut: [Rollenbezeichnung + Begründung]
- Könnte passen: [Rollenbezeichnung + Begründung]
- Entwicklungsperspektive: [Rollenbezeichnung + Begründung]
(Achte darauf, dass fachliche Eignung und persönliche Rahmenbedingungen wie Schicht, Reisebereitschaft oder Remote getrennt bewertet werden).

6. KOMPETENZLÜCKEN
- Welche Qualifikationen oder Kenntnisse fehlen für die jeweiligen Zielrollen noch?

7. HANDLUNGS-ROADMAP
- Heute: Was ist vorhanden?
- Nächster Schritt: Kurze, konkrete Maßnahme.
- Entwicklung: Schließen der Lücke.
- Perspektive: Langfristige Möglichkeit.
"""

# HELPER FUNCTIONS
def extract_text_from_pdf(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

# UI & UPLOAD
st.subheader("Dokumente hochladen & analysieren")

uploaded_files = st.file_uploader(
    "Lebenslauf, Zeugnisse, Zertifikate oder Tätigkeitsbeschreibungen (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

additional_notes = st.text_area(
    "Zusätzliche Rahmenbedingungen oder persönliche Wünsche (optional):",
    placeholder="z. B. Keine Schichtarbeit mehr gewünscht, Fokus auf Fachberatung statt Führung, max. 20 % Reisebereitschaft..."
)

if st.button("Analyse starten", type="primary"):
    if not uploaded_files and not additional_notes:
        st.warning("Bitte lade mindestens ein PDF-Dokument hoch oder gib Kontext ein.")
    else:
        with st.spinner("Dokumente werden gelesen und strukturiert ausgewertet..."):
            combined_text = ""
            for pdf in uploaded_files:
                combined_text += f"\n--- INHALT DATEI: {pdf.name} ---\n"
                combined_text += extract_text_from_pdf(pdf)
            
            if additional_notes:
                combined_text += f"\n--- ZUSÄTZLICHER KONTEXT / RAHMENBEDINGUNGEN ---\n{additional_notes}"

            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"Hier sind die zu analysierenden Dokumente und Informationen:\n\n{combined_text}",
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2
                    )
                )
                
                st.success("Analyse erfolgreich abgeschlossen!")
                st.markdown("---")
                st.markdown(response.text)
                
                st.download_button(
                    label="Ergebnis als Textdatei herunterladen",
                    data=response.text,
                    file_name="Rollen_und_Kompetenzportfolio.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Fehler bei der Analyse: {str(e)}")
