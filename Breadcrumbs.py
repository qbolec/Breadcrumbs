# -*- coding: utf-8 -*-
import re
import html

import sublime
import sublime_plugin

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


def get_breadcrumb(view, points, regex, limit):
  linestring = view.substr(sublime.Region(min(points), min(view.line(min(points)).b, min(points) + limit)))
  match = re.search(regex, linestring)
  if match:
    return(match.group('name'))
  else:
    return ''


def make_breadcrumbs(view, current_row, shorten):
  if len(view.sel()) == 0:
    return

  settings = sublime.load_settings('Breadcrumbs.sublime-settings')
  tab_size = get_tab_size(view)
  default_breadcrumb_regex = settings.get('breadcrumb_regex', u'^\s*(?P<name>.*\\S)')
  breadcrumb_regex = view.settings().get('breadcrumb_regex', default_breadcrumb_regex)
  separator = settings.get('breadcrumbs_separator', u' › ')
  breadcrumb_length_limit = settings.get('breadcrumb_length_limit', 100)
  total_breadcrumbs_length_limit = settings.get('total_breadcrumbs_length_limit', 200)

  def get_row_start(row):
    return view.text_point(row, 0)

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
      this_breadcrumb = get_breadcrumb(view, points, breadcrumb_regex, breadcrumb_length_limit)
      if not this_breadcrumb == '':
        breadcrumbs.append(this_breadcrumb)

    current_row -= 1

  breadcrumbs.reverse()

  if shorten:
    lengths = [len(breadcrumb) for breadcrumb in breadcrumbs]
    sorted_lengths = sorted(lengths)
    previous_length = 0
    number_of_characters_left = total_breadcrumbs_length_limit - len(lengths) * len(separator)
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

  return breadcrumbs


def copy(view, text):
  sublime.set_clipboard(text)
  view.hide_popup()
  sublime.status_message('Breadcrumbs copied to clipboard')


class BreadcrumbsCommand(sublime_plugin.EventListener):

  def on_selection_modified(self, view):
    settings = sublime.load_settings('Breadcrumbs.sublime-settings')
    view.erase_status('breadcrumbs')
    if settings.get('breadcrumbs_statusbar', True):
      separator = settings.get('breadcrumbs_separator', u' › ')
      current_row = view.rowcol(view.sel()[0].b)[0]
      breadcrumbs = make_breadcrumbs(view, current_row, False)
      if breadcrumbs is not None and len(breadcrumbs) > 0:
        view.set_status('breadcrumbs', separator.join(make_breadcrumbs(view, current_row, True)))


class BreadcrumbsPopupCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    stylesheet = '''
      p {
        margin-top: 0;
      }
      a {
        font-family: system;
        font-size: 1.05rem;
      }
    '''

    template = '''
      <body id=show-scope>
          <style>{stylesheet}</style>
          <p>{breadcrumbs}</p>
          <a href="copy">Copy</a>
      </body>
    '''

    settings = sublime.load_settings('Breadcrumbs.sublime-settings')
    separator = settings.get('breadcrumbs_separator', u' › ')
    view = self.view
    current_row = view.rowcol(view.sel()[0].b)[0]
    breadcrumbs = make_breadcrumbs(view, current_row, False)
    escaped_crumbs = []
    if len(breadcrumbs) > 0:
      for crumb in breadcrumbs:
        escaped_crumbs.append(html.escape(crumb, quote=False))
      breadcrumbs_element = '<br>'.join(escaped_crumbs)
    else:
      breadcrumbs_element = '<em>None</em>'

    breadcrumbs_string = separator.join(breadcrumbs)
    body = template.format(
        breadcrumbs=breadcrumbs_element,
        stylesheet=stylesheet
    )
    view.show_popup(body, max_width=512, on_navigate=copy(view, breadcrumbs_string))

  def is_visible(self):
    return int(sublime.version()) > 3124


class BreadcrumbsPhantomCommand(sublime_plugin.TextCommand):

  def __init__(self, view):
    self.phantoms_visible = False
    self.view = view
    self.phantom_set = sublime.PhantomSet(view, 'breadcrumbs')

  def close_phantoms(self, href):
    if href is not 'close':
      copy(self.view, href)
    self.view.erase_phantoms('breadcrumbs')
    self.phantoms_visible = False

  def run(self, edit):
    if self.phantoms_visible:
      self.close_phantoms('close')
      return
    else:
      self.close_phantoms('close')

    stylesheet = '''
      <style>
        html {
          --base-bg: color(var(--bluish) blend(var(--background) 30%));
          --accent-bg: color(var(--base-bg) blend(var(--foreground) 90%));
          line-height: 20px;
        }
        div.phantom {
          margin: 0;
        }
        .crumb {
          line-height: 2em;
          padding-right: 6px;
        }
        .separator {
          border: 1em solid;
          width: 0;
          height: 0;
          font-size: inherit;
          line-height: 0px;
        }
        .crumb-1,
        .separator-1 {
          background-color: var(--base-bg);
        }
        .crumb-2,
        .separator-2 {
          background-color: var(--accent-bg);
        }
        .separator-1 {
          border-color: var(--base-bg);
          border-left-color: var(--accent-bg);
        }
        .separator-2 {
          border-color: var(--accent-bg);
          border-left-color: var(--base-bg);
        }
        div.phantom a {
          text-decoration: inherit;
          vertical-align: middle;
          line-height: 2em;
          padding: 0 7px 0 12px;
          background-color: var(--base-bg);
        }
        div.phantom a.close {
          font-weight: bold;
          padding-left: 4px;
        }
      </style>
    '''

    template = '''
      <body id="inline-breadcrumbs">
        {stylesheet}
        <div class="phantom">{breadcrumbs}<a href="{breadcrumbs_string}">Copy</a><a class="close" href="close">''' + chr(0x00D7) + '''</a></div>
      </body>
    '''
    settings = sublime.load_settings('Breadcrumbs.sublime-settings')
    separator = settings.get('breadcrumbs_separator', u' › ')
    phantoms = []

    for region in self.view.sel():
      (row, col) = self.view.rowcol(region.begin())

      crumb_elements = []
      for i, crumb in enumerate(make_breadcrumbs(self.view, row, False)):
        parity = (i % 2) + 1
        crumb_elements.append('<span class="separator separator-{parity}"> </span><span class="crumb crumb-{parity}">'.format(parity=parity) + html.escape(crumb, quote=False) + '</span>')

      body = template.format(
          breadcrumbs=''.join(crumb_elements),
          breadcrumbs_string=html.escape(separator.join(make_breadcrumbs(self.view, row, False)), quote=True),
          stylesheet=stylesheet
      )
      phantom = sublime.Phantom(
          region,
          body,
          sublime.LAYOUT_BLOCK,
          self.close_phantoms
      )
      phantoms.append(phantom)

    self.phantom_set.update(phantoms)
    self.phantoms_visible = True

  def is_visible(self):
    return int(sublime.version()) > 3124
