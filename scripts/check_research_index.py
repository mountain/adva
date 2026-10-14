"""Reject incomplete research indexes before builds or focused experiment checks."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_index(text, research):
    """Compare link targets and declared counts with the actual inventory."""
    numbered = {p.name for p in research.glob('[0-9][0-9][0-9][0-9]-*.md')}
    named = {p.name for p in research.glob('*.md')} - numbered - {'README.md'}
    directories = {p.name + '/' for p in research.iterdir()
                   if p.is_dir() and not p.name.startswith('__')}
    linked = set(re.findall(r'\]\(([A-Za-z0-9._/-]+)\)', text))
    errors = []
    for label, inventory in [('numbered notes', numbered), ('named notes', named),
                             ('supporting directories', directories)]:
        missing = sorted(inventory - linked)
        if missing:
            errors.append(f'{label} missing: {missing}')
    dangling = sorted(target for target in linked
                      if '/' not in target and not (research / target).exists())
    if dangling:
        errors.append(f'dangling links: {dangling}')
    counts = re.search(r'\*\*(\d+) numbered\s+notes, (\d+) named notes and '
                       r'(\d+) supporting directories\*\*', text)
    actual = (len(numbered), len(named), len(directories))
    if not counts or tuple(map(int, counts.groups())) != actual:
        errors.append(f'header counts do not match inventory {actual}')
    identity = '../RESEARCH_REFERENCE_IDENTITY.md'
    if identity not in linked:
        errors.append('reference identity entry missing')
    return errors


if __name__ == '__main__':
    research = ROOT / 'docs/research'
    errors = validate_index((research / 'README.md').read_text(encoding='utf-8'), research)
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Research index: complete inventory, counts and reference identity entry checked.')
