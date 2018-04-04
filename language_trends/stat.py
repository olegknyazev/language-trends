from . import data
from .languages import ALL_LANGUAGES

def format_stats(stats):
  stats = [('Language', '# Repos', '# Commits')] + stats
  return '\n'.join('{:20} | {:>8} | {:>12}'.format(*l) for l in stats)

def main():
  print(format_stats(data.language_stats(ALL_LANGUAGES)))

if __name__ == '__main__':
  main()
