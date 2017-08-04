# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import math
import re

try:
  xrange
except NameError:
  xrange = range

def get_tab_size(view):
  return int(view.settings().get('tab_size', 8))

def get_row_indentation(points, view, tab_size, limit=1e20):
  pos = 0
  for pt in points:
    ch = view.substr(pt)

    if ch == '\t':
      pos += tab_size - (pos % tab_size)

    elif ch.isspace():
      pos += 1

    else:
      break

    if limit <= pos:
      break

  return pos

def is_white_row(view, points):
  return all(view.substr(pt).isspace() for pt in reversed(points))

def get_breadcrumb(view, points, regex, separator):
  for pt in points:
    ch = view.substr(pt)
    if not ch.isspace():
      linestring = view.substr(sublime.Region(pt, min(view.line(pt).b, pt + 500))).strip()
      match = re.search(re.compile(regex), linestring)
      if match:
        return(separator + match.group('name'))
  return ''

class BreadcrumbsCommand(sublime_plugin.EventListener):
  def on_selection_modified_async(self, view):
    tab_size = get_tab_size(view)
    settings = sublime.load_settings('Breadcrumbs.sublime-settings')
    my_regex = settings.get('breadcrumbs_regex', u'(?P<name>.*)')
    breadcrumb_length_limit = settings.get('breadcrumb_length_limit', 100)
    separator = settings.get('breadcrumbs_separator', u' › ')
    total_breadcrumbs_length_limit = settings.get('total_breadcrumbs_length_limit', 200)

    view.erase_status('breadcrumbs')

    if len(view.sel()) == 0:
      return

    current_row = view.rowcol(view.sel()[0].b)[0]

    def get_row_start(row):
      return view.text_point(row,0)

    def get_points_by_row(row):
      return xrange(get_row_start(row), get_row_start(row + 1))

    if is_white_row(view, get_points_by_row(current_row)):
      while 0 <= current_row and is_white_row(view, get_points_by_row(current_row)):
        current_row -= 1

      if current_row < 0:
        return

      indentation = get_row_indentation(get_points_by_row(current_row), view, tab_size) + 1
    else:
      indentation = get_row_indentation(get_points_by_row(current_row), view, tab_size)
      current_row -= 1

    breadcrumbs = []
    last_line_start = view.text_point(current_row + 1, 0)
    while 0 <= current_row and 0 < indentation:
      line_start = get_row_start(current_row)
      points = xrange(line_start, last_line_start)
      last_line_start = line_start
      current_indentation = get_row_indentation(points, view, tab_size, indentation)
      if current_indentation < indentation and not is_white_row(view, points):
        indentation = current_indentation
        breadcrumbs.append(get_breadcrumb(view, points, my_regex, separator))

      current_row -= 1

    breadcrumbs.reverse()
    lengths = [len(breadcrumb) for breadcrumb in breadcrumbs]
    sorted_lengths = sorted(lengths)
    previous_length = 0
    number_of_characters_left  = total_breadcrumbs_length_limit - len(lengths) * len(separator)
    for (number_of_shorter, current_length) in enumerate(sorted_lengths):
      if previous_length < current_length:
        previous_length = current_length
        number_of_not_shorter = len(breadcrumbs) - number_of_shorter
        if number_of_characters_left < current_length * number_of_not_shorter:
          length_of_short_trim = number_of_characters_left // number_of_not_shorter
          length_of_long_trim = length_of_short_trim + 1
          number_of_long_trimmed = number_of_characters_left % number_of_not_shorter
          number_of_short_trimmed = number_of_not_shorter - number_of_long_trimmed
          for (index_of_breadcrumb, breadcrum_length) in enumerate(lengths):
            if current_length <= breadcrum_length:
              if 0 < number_of_short_trimmed:
                length_of_trim = length_of_short_trim
                number_of_short_trimmed -= 1
              else:
                length_of_trim = length_of_long_trim
              breadcrumbs[index_of_breadcrumb] = breadcrumbs[index_of_breadcrumb][0:length_of_trim]
          break
      number_of_characters_left -= current_length
    view.set_status('breadcrumbs',''.join(breadcrumbs+['']))
