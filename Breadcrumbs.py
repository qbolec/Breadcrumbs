# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import math

try:
  xrange
except NameError:
  xrange = range

def get_tab_size(view):
  return int(view.settings().get('tab_size', 8))

def get_line_by_row(view, row):
  return view.line(view.text_point(row,0))

def points_of_line(line):
  return xrange(line.begin(), line.end())

def get_row_indentation(view, row):
  tab_size = get_tab_size(view)
  pos = 0
  ln = get_line_by_row(view,row)

  for pt in points_of_line(ln):
    ch = view.substr(pt)

    if ch == '\t':
      pos += tab_size - (pos % tab_size)

    elif ch.isspace():
      pos += 1

    else:
      break

  return pos

def is_white_row(view, row):
  line = get_line_by_row(view,row)
  return all(view.substr(pt).isspace() for pt in points_of_line(line))

def get_breadcrumb(view, line, limit):
  for pt in points_of_line(line):
    ch = view.substr(pt)
    if not ch.isspace():
      return view.substr(sublime.Region(pt,min(line.b,pt + limit))).strip()
  return ''

class BreadcrumbsCommand(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        settings = sublime.load_settings('Breadcrumbs.sublime-settings')
        breadcrumb_length_limit = settings.get('breadcrumb_length_limit', 100)
        separator = settings.get('breadcrumbs_separator', u' ■ ')
        total_breadcrumbs_length_limit = settings.get('total_breadcrumbs_length_limit', 200)
        view.erase_status('breadcrumbs')
        current_row = None
        for region in view.sel():
          current_row = view.rowcol(region.b)[0]
          break

        if current_row is None:
          return

        if is_white_row(view, current_row):
          while 0 <= current_row and is_white_row(view, current_row):
            current_row -= 1

          if current_row < 0:
            return

          indentation = get_row_indentation(view, current_row) + 1          
        else:
          indentation = get_row_indentation(view, current_row)
          current_row -= 1

        breadcrumb_lines = []
        while 0<=current_row and 0<indentation:
          if not is_white_row(view, current_row):
            current_indentation = get_row_indentation(view, current_row)

            if current_indentation < indentation:
              indentation = current_indentation
              breadcrumb_lines.append(get_line_by_row(view,current_row))

          current_row -= 1

        breadcrumbs = [
          get_breadcrumb(view, breadcrumb_line, breadcrumb_length_limit)
          for breadcrumb_line in reversed(breadcrumb_lines)
        ]

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

        view.set_status('breadcrumbs',separator.join(breadcrumbs+['']))

