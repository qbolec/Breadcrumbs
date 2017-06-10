# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import math

def get_tab_size(view):
  return int(view.settings().get('tab_size', 8))

def get_line_by_row(view, row):
  return view.line(view.text_point(row,0))

def get_row_indentation(view, row):
  tab_size = get_tab_size(view)
  pos = 0
  ln = get_line_by_row(view,row)

  for pt in xrange(ln.begin(), ln.end()):
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
  return all(view.substr(pt).isspace() for pt in xrange(line.begin(), line.end()))

def get_breadcrumb(view, line, limit):
  for pt in xrange(line.begin(), line.end()):
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

        while 0 <= current_row and is_white_row(view, current_row):
          current_row -= 1

        if current_row < 0:
          return

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
        needed_chars = sum(lengths) + (len(lengths)) * len(separator)
        overflow = needed_chars - total_breadcrumbs_length_limit
        while 0 < overflow:
          max_length = max(lengths)
          equal = len([0 for length in lengths if length == max_length ])
          next_length = max([0]+[length for length in lengths if length < max_length ])
          if overflow <= equal:
            cut = 1
          else:
            cut = min(max_length - next_length, overflow // equal )

          for (i, length) in enumerate(lengths):
            if length == max_length:
              lengths[i] -= cut
              overflow -= cut
              breadcrumbs[i] = breadcrumbs[i][:-cut]
              if overflow <= 0:
                break
        view.set_status('breadcrumbs',separator.join(breadcrumbs+['']))

