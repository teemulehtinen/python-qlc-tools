#!/usr/bin/env python3
import random
from analyser import Analyser

BUILT_IN_SELECTION = [
  'abs','all','any','bool','dict','float','input','int','len','list',
  'max','min','object','open','print','range','reversed','round','set',
  'sorted','sum','tuple','zip'
]

DISTRACTOR_WORDS = [
  'total', 'other', 'foo', 'bar', 'n', 'tmp', 'magic', 'temp', 'important'
]

TEXTS = {
  'en': {
    
    'select_variables': 'Which of the following are variable names in the program?',
    'variable': 'A variable in the program',
    'reserved_word': 'A reserved word in programming language',
    'unused_word': 'This word was not used in the program',
    'built_in_function': 'A function that is built in to programming language',

    'select_raise_line': 'From which line program execution may continue to line {:d}?',
    'from_line': 'Line {:d}',
    'try_line_before': 'Except-block cannot be entered from outside the corresponding try-block',
    'try_line_try': 'At least the first line inside try-block starts executing',
    'try_line_ok': 'This line can rise a matching error',
    'try_line_no': 'This line should not rise a matching error',

    'select_purpose': 'Which of the following best describes the purpose of line {:d}?',
    'purpose_guard_zero': 'Guards against division by zero',
    'purpose_end_program': 'Is a condition for ending program',
    'purpose_negative_input': 'Ignores negative input',
    'purpose_accepts_new_data': 'Accepts new data'
  },
  'fi': {
    
    'select_variables': 'Mitkä seuraavista ovat muuttujien nimiä ohjelmassa?',
    'variable': 'Muuttuja tässä ohjelmassa',
    'reserved_word': 'Varattu sana ohjelmointikielessä',
    'unused_word': 'Käyttämätön sana tässä ohjelmassa',
    'built_in_function': 'Funktio, joka on määritelty ohjelmointikielen sisään',
    
    'select_raise_line': 'Miltä riviltä ohjelman suoritus voi siirtyä riville {:d}?',
    'from_line': 'Riviltä {:d}',
    'try_line_before': 'Except-lohkoon ei voida siirtyä vastaavan try-lohkon ulkopuolelta',
    'try_line_try': 'Vähintään try-lohkon ensimmäistä riviä aletaan suorittaa',
    'try_line_ok': 'Tämä rivi voi aiheuttaa yhteensopivan virheen',
    'try_line_no': 'Tämän rivin ei pitäisi aiheuttaa yhteensopivaa virhettä',

    'select_purpose': 'Mikä seuraavista kuvaa parhaiten rivin {:d} tarkoitusta?',
    'purpose_guard_zero': 'Suojaa nollalla jakamiselta',
    'purpose_end_program': 'On ehto ohjelman loppumiselle',
    'purpose_negative_input': 'Ohittaa negatiivisen syötteen',
    'purpose_accepts_new_data': 'Vastaanottaa uutta syötettä'
  }
}

def t(lang, key):
  return TEXTS[lang][key]

def opt_purpose(typ, ok, lang='en'):
  return {
    'label': t(lang, typ),
    'value': typ + ('_ok' if ok else ''),
    'correct': ok
  }

def q_names(analysis, lang='en'):
  data = analysis.get('NamesCollector', [])
  def by_type(typ):
    return list(set(n for n, l, t in data if t == typ))
  variables = by_type('variable_store')
  reserved_words = by_type('reserved_word')
  unused_words = list(n for n in DISTRACTOR_WORDS if not n in variables)
  built_ins = list(n for n in by_type('other_load') if n in BUILT_IN_SELECTION)
  options = []
  def opt(nam, typ):
    options.append({
      'label': nam,
      'value': typ + '_' + nam,
      'message': t(lang, typ),
      'correct': typ == 'variable'
    })
  for n in random.sample(variables, min(2, len(variables))):
    opt(n, 'variable')
  for n in random.sample(reserved_words, min(1, len(reserved_words))):
    opt(n, 'reserved_word')
  for n in random.sample(unused_words, min(1, len(unused_words))):
    opt(n, 'unused_word')
  for n in random.sample(built_ins, min(5 - len(options), len(built_ins))):
    opt(n, 'built_in_function')
  random.shuffle(options)
  return {
    'question': t(lang, 'select_variables'),
    'options': options
  }

def q_try_except(analysis, lang='en'):
  data = analysis.get('TryExceptDetector', [])
  valid_cases = list(c for c in data if len(c['causes']) > 0)
  if len(valid_cases) == 0:
    return None
  case = random.choice(valid_cases)
  all_lines = range(case['try'] + 1, case['except'])
  cause_lines = list(c[1] for c in case['causes'])
  no_lines = list(n for n in all_lines if not n in cause_lines)
  def opt(line, typ):
    return {
      'label': t(lang, 'from_line').format(line),
      'value': typ + '_' + str(line),
      'message': t(lang, typ),
      'correct': typ == 'try_line_ok'
    }
  options = [
    opt(case['try'] - random.choice(range(1, 4)), 'try_line_before'),
    opt(case['try'], 'try_line_try'),
    opt(random.choice(cause_lines), 'try_line_ok')
  ]
  if len(no_lines) > 1:
    options.append(opt(random.choice(no_lines), 'try_line_no'))
  random.shuffle(options)
  return {
    'question': t(lang, 'select_raise_line').format(case['except']),
    'options': options
  }

def q_guard_zero_division(analysis, lang='en'):
  data = analysis.get('IfGuardZeroDivision', [])
  if len(data) == 0:
    return None
  case = random.choice(data)
  options = [
    opt_purpose('purpose_guard_zero', True, lang),
    opt_purpose('purpose_end_program', False, lang),
    opt_purpose('purpose_negative_input', False, lang),
    opt_purpose('purpose_accepts_new_data', False, lang)
  ]
  random.shuffle(options)
  return {
    'question': t(lang, 'select_purpose').format(case['if']),
    'options': options
  }

def q_accept_input(analysis, lang='en'):
  data = analysis.get('NamesCollector', [])
  other_loads = list(set((n, l) for n, l, t in data if t == 'other_load'))
  input_lines = list(l for n, l in other_loads if n == 'input')
  if len(input_lines) == 0:
    return None
  case = random.choice(input_lines)
  options = [
    opt_purpose('purpose_guard_zero', False, lang),
    opt_purpose('purpose_end_program', False, lang),
    opt_purpose('purpose_negative_input', False, lang),
    opt_purpose('purpose_accepts_new_data', True, lang)
  ]
  random.shuffle(options)
  return {
    'question': t(lang, 'select_purpose').format(case),
    'options': options
  }

def generate_qlcs(analysis, lang='en'):
  return list(
    q for q in [
      q_names(analysis, lang),
      q_try_except(analysis, lang),
      q_guard_zero_division(analysis, lang),
      q_accept_input(analysis, lang)
    ] if not q is None
  )

def qlcs_for_files(file_name_list):
  import json
  analyser = Analyser.full_analysis()
  for file_name in file_name_list:
    print('=== {} ==='.format(file_name))
    analysis = analyser.analyse_source_file(file_name)
    print(json.dumps(generate_qlcs(analysis, 'en'), indent=4))

if __name__ == "__main__":
	import sys
	if len(sys.argv) == 1:
		print("Usage: {} [pythonsourcefiles]".format(sys.argv[0]))
	else:
		qlcs_for_files(sys.argv[1:])
