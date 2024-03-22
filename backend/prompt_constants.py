import typing

PROMPT_DE: typing.Final[str] = (
    "Deine Antwort sollte kurz, sachlich, klar und ohne Abkürzungen sein, "
    "sodass sie für Text-zu-Sprache-Lesegeräte geeignet ist. "
    "Schließe auch gesprächsähnliche Elemente wie 'nun,' 'sehen Sie,' oder "
    "ähnliche Phrasen ein, um die Antwort natürlicher klingen zu lassen. Falls "
    "die Antwort nicht im Text angegeben wurde, um exakt die Frage zu "
    "beantworten, stelle das klar. Gebe mir eine Antwort basierend NUR auf die "
    "angegebenen Informationen. Du darfst kein Wissen benutzen das nicht im Text stand."
)

PROMPT_TEMPLATE_DE: typing.Final[str] = ("""
{context}
-----
""" + PROMPT_DE + """
Frage: {question}
Antwort: """)
