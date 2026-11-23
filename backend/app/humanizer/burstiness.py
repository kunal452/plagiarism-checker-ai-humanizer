import re
from typing import List

class BurstinessTransformer:
    """
    Adjusts sentence cadence and syntactic variability:
    - Breaks uniform sentence pacing into dynamic short-and-long rhythms
    - Injects stylistic variance (staccato punchy clauses, parentheticals, em-dashes)
    - Re-balances repetitive subject-verb sentence openings
    """

    @classmethod
    def inject_rhythm_variation(cls, sentences: List[str], intensity: str = "balanced") -> List[str]:
        """
        Takes a list of sentences and modulates their lengths and transitions.
        """
        if not sentences:
            return []

        modified = []
        i = 0
        n = len(sentences)

        while i < n:
            s = sentences[i].strip()
            words = s.split()

            # If sentence is very long (>30 words), split it into a punchy lead and explanation
            if len(words) > 28 and (intensity in ["balanced", "aggressive"]):
                split_points = [m.start() for m in re.finditer(r',\s+(?:which|where|because|although|while|since)\s+', s)]
                if split_points:
                    pt = split_points[0]
                    part1 = s[:pt].strip()
                    part2 = s[pt:].strip()
                    part2_clean = re.sub(r'^,\s*(?:which|where|because|although|while|since)\s*', '', part2)
                    if part2_clean:
                        part2_clean = part2_clean[0].upper() + part2_clean[1:]
                    modified.append(part1 + ".")
                    if part2_clean:
                        modified.append(part2_clean)
                    i += 1
                    continue

            # If two consecutive sentences are short (<10 words), sometimes combine them with em-dash or semicolon
            if i + 1 < n:
                next_s = sentences[i + 1].strip()
                if len(words) < 8 and len(next_s.split()) < 12 and (intensity in ["balanced", "aggressive"]):
                    combined = f"{s.rstrip('.')} — {next_s[0].lower() + next_s[1:]}"
                    modified.append(combined)
                    i += 2
                    continue

            modified.append(s)
            i += 1

        return modified
