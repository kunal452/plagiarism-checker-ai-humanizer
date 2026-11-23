import re
from typing import Tuple, List, Dict

class AIClicheSanitizer:
    """
    Identifies and replaces formulaic LLM filler words and transition clichés
    with authentic, natural human phrasing.
    """

    REPLACEMENTS = [
        # Formulaic transitions
        (r'\bIn conclusion,\s*', ['Overall, ', 'Ultimately, ', 'In short, ', 'To wrap up, ']),
        (r'\bMoreover,\s*', ['Also, ', 'Beyond that, ', 'At the same time, ', 'In addition, ']),
        (r'\bFurthermore,\s*', ['What is more, ', 'On top of that, ', 'Plus, ', 'Beyond this, ']),
        (r'\bIt is important to note that\s+', ['Notice that ', 'Importantly, ', 'Crucially, ', 'Note that ']),
        (r'\bIt is worth noting that\s+', ['Interestingly, ', 'Notably, ', 'Keep in mind that ']),
        (r'\bIt is crucial to remember that\s+', ['We must remember that ', 'Remember that ', 'Crucially, ']),
        (r'\bIn the modern era,\s*', ['Today, ', 'Recently, ', 'Nowadays, ', 'In recent years, ']),
        (r'\bIn today\'s fast-paced world,\s*', ['Today, ', 'Currently, ', 'Now, ']),

        # Cliché adjectives and nouns
        (r'\bdelve into\b', ['examine', 'explore', 'look into', 'investigate', 'analyze']),
        (r'\bdelves into\b', ['examines', 'explores', 'looks into', 'investigates']),
        (r'\bdelving into\b', ['examining', 'exploring', 'looking into']),
        (r'\ba testament to\b', ['clear proof of', 'strong evidence for', 'an indicator of']),
        (r'\brich tapestry\b', ['complex mix', 'wide array', 'diverse mosaic']),
        (r'\bmultifaceted\b', ['complex', 'many-sided', 'varied', 'layered']),
        (r'\bpivotal role\b', ['key role', 'major part', 'central role']),
        (r'\bparamount importance\b', ['high importance', 'critical value', 'key priority']),
        (r'\bbeacon of\b', ['model for', 'hallmark of', 'symbol of']),
        (r'\bgame-changer\b', ['major shift', 'turning point', 'breakthrough']),
        (r'\bharness the power of\b', ['leverage', 'make use of', 'apply', 'employ']),
        (r'\bstands as a testament\b', ['shows clearly', 'proves', 'demonstrates']),
        (r'\bunraveling the mysteries\b', ['understanding', 'figuring out', 'decoding']),
    ]

    @classmethod
    def sanitize(cls, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Replaces detected clichés and returns cleaned text with substitution logs.
        """
        cleaned_text = text
        substitutions = []

        for pattern, options in cls.REPLACEMENTS:
            def repl(match):
                replacement = options[0]
                substitutions.append({
                    "original": match.group(0),
                    "replacement": replacement
                })
                # Preserve capitalization
                if match.group(0)[0].isupper() and len(replacement) > 0:
                    replacement = replacement[0].upper() + replacement[1:]
                return replacement

            cleaned_text = re.sub(pattern, repl, cleaned_text, flags=re.IGNORECASE)

        return cleaned_text, substitutions
