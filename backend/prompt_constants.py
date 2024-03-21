import typing


PROMPT_DE: typing.Final[str] = (
    "Bitte geben Sie eine prägnante und sachliche Antwort auf die Frage, "
    "basierend auf dem gegebenen Kontext. Ihre Antwort sollte klar sein und "
    "komplexe Formatierungen vermeiden, sodass sie für "
    "Text-zu-Sprache-Lesegeräte geeignet ist. Schließen Sie gesprächsähnliche "
    "Elemente wie 'nun,' 'sehen Sie,' oder ähnliche Phrasen ein, um die "
    "Antwort natürlicher klingen zu lassen. Falls Sie nicht genügend "
    "Informationen haben, um genau zu antworten, stellen Sie das bitte klar "
    "und schlagen Sie vor, wen ich für eine informiertere Antwort kontaktieren "
    "könnte, und erklären Sie, warum diese Person besser geeignet wäre, zu "
    "antworten. Konzentrieren Sie sich darauf, die sachliche Wahrheit "
    "basierend auf den folgenden Kontextstücken zu liefern:"
)

PROMPT_TEMPLATE_DE: typing.Final[str] = PROMPT_DE + \
    """
    
    {context}
    -----
    Frage: {question}
    Antwort:"""