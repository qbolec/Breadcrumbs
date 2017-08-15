# -*- coding: utf-8 -*-
import re
import sublime
import sublime_plugin

if int(sublime.version()) > 3124:
  import html

try:
  xrange
except NameError:
  xrange = range


def get_tab_size(view):
  return int(view.settings().get('tab_size', 8))


def get_row_indentation(line_start, view, tab_size, indentation_limit=None):
  if indentation_limit is None:
    row = view.rowcol(line_start)[0]
    indentation_limit = view.text_point(row + 1, 0) - line_start

  pos = 0
  for ch in view.substr(sublime.Region(line_start, line_start + indentation_limit)):
    if ch == '\t':
      pos += tab_size - (pos % tab_size)

    elif ch == ' ':
      pos += 1

    else:
      break

    if indentation_limit <= pos:
      break

  return pos


def is_white_row(view, points):
  return all(view.substr(pt).isspace() for pt in reversed(points))


def get_separator(view):
  settings = sublime.load_settings('Breadcrumbs.sublime-settings')
  default_separator = settings.get('breadcrumbs_separator', u' ')
  separator = view.settings().get('breadcrumbs_separator', default_separator)
  return separator


def get_breadcrumb(view, line_start, line_end, regex, limit):
  linestring = view.substr(sublime.Region(line_start, min(line_end, line_start + 1024)))
  match = re.search(regex, linestring)
  if match:
    return match.group('name')[0:limit]
  else:
    return None


def make_breadcrumbs(view, current_row, shorten=False):
  if len(view.sel()) == 0:
    return []

  settings = sublime.load_settings('Breadcrumbs.sublime-settings')
  tab_size = get_tab_size(view)

  default_breadcrumb_regex = settings.get('breadcrumb_regex', u'(?P<name>.*)')
  breadcrumb_regex = view.settings().get('breadcrumb_regex', default_breadcrumb_regex)

  breadcrumb_length_limit = settings.get('breadcrumb_length_limit', 100)

  def get_row_start(row):
    return view.text_point(row, 0)

  def get_points_by_row(row):
    return xrange(get_row_start(row), get_row_start(row + 1))

  if is_white_row(view, get_points_by_row(current_row)):
    while 0 <= current_row and is_white_row(view, get_points_by_row(current_row)):
      current_row -= 1

    if current_row < 0:
      return []

    indentation = get_row_indentation(get_row_start(current_row), view, tab_size) + 1
  else:
    indentation = get_row_indentation(get_row_start(current_row), view, tab_size)
    current_row -= 1

  breadcrumbs = []
  last_line_start = view.text_point(current_row + 1, 0)
  while 0 <= current_row and 0 < indentation:
    line_start = get_row_start(current_row)
    line_end = last_line_start
    last_line_start = line_start
    current_indentation = get_row_indentation(line_start, view, tab_size, indentation)
    if current_indentation < indentation and not is_white_row(view, xrange(line_start, line_end)):
      indentation = current_indentation
      this_breadcrumb = get_breadcrumb(view, line_start, line_end, breadcrumb_regex, breadcrumb_length_limit)
      if this_breadcrumb is not None:
        breadcrumbs.append(this_breadcrumb)

    current_row -= 1

  breadcrumbs.reverse()
  if shorten:
    total_breadcrumbs_length_limit = settings.get('total_breadcrumbs_length_limit', 200)
    lengths = [len(breadcrumb) for breadcrumb in breadcrumbs]
    sorted_lengths = sorted(lengths)
    previous_length = 0
    number_of_characters_left = max(0, total_breadcrumbs_length_limit - len(lengths) * len(get_separator(view)))
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
  sublime.status_message('Breadcrumbs copied to clipboard')


class BreadcrumbsEventListener(sublime_plugin.EventListener):

  def on_selection_modified(self, view):
    view.erase_status('breadcrumbs')

    settings = sublime.load_settings('Breadcrumbs.sublime-settings')
    default_statusbar_enabled = settings.get('show_breadcrumbs_in_statusbar', True)
    statusbar_enabled = view.settings().get('show_breadcrumbs_in_statusbar', default_statusbar_enabled)

    if statusbar_enabled:
      current_row = view.rowcol(view.sel()[0].b)[0]
      breadcrumbs = make_breadcrumbs(view, current_row, shorten=True)

      if len(breadcrumbs) > 0:
        view.set_status('breadcrumbs', get_separator(view).join(breadcrumbs))


class BreadcrumbsPopupCommand(sublime_plugin.TextCommand):

  def run(self, edit):

    '''
    Built to look and work like the ShowScopeName command's popup
    See show_scope_name.py in the Default package
    '''

    stylesheet = '''
      p {
        margin-top: 0;
      }
      a {
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

    view = self.view
    current_row = view.rowcol(view.sel()[0].b)[0]
    breadcrumbs = make_breadcrumbs(view, current_row)
    escaped_crumbs = []
    if len(breadcrumbs) > 0:
      for crumb in breadcrumbs:
        escaped_crumbs.append(html.escape(crumb, quote=False))
      breadcrumbs_element = '<br>'.join(escaped_crumbs)
    else:
      breadcrumbs_element = '<em>None</em>'

    breadcrumbs_string = get_separator(view).join(breadcrumbs)
    body = template.format(
        breadcrumbs=breadcrumbs_element,
        stylesheet=stylesheet
    )
    view.show_popup(
        body,
        max_width=512,
        on_navigate=lambda x: [
            copy(view, breadcrumbs_string),
            view.hide_popup()
        ]
    )

  def is_visible(self):
    return int(sublime.version()) > 3124


class BreadcrumbsPhantomCommand(sublime_plugin.TextCommand):

  def __init__(self, view):
    self.phantoms_visible = False
    self.view = view
    self.phantom_set = sublime.PhantomSet(view, 'breadcrumbs')

  def close(self):
    self.view.erase_phantoms('breadcrumbs')
    self.phantoms_visible = False

  def navigate(self, href, breadcrumbs_string):
    if href == 'close':
      self.close()
    else:
      copy(self.view, breadcrumbs_string)

  def run(self, edit):
    if self.phantoms_visible:
      self.close()
      return

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
        <div class="phantom">{breadcrumbs}<a href="copy">Copy</a><a class="close" href="close">''' + chr(0x00D7) + '''</a></div>
      </body>
    '''

    phantoms = []

    for region in self.view.sel():
      (row, col) = self.view.rowcol(region.begin())

      crumb_elements = []
      breadcrumbs = make_breadcrumbs(self.view, row)
      for i, crumb in enumerate(breadcrumbs):
        parity = (i % 2) + 1
        crumb_elements.append('<span class="separator separator-{parity}"> </span><span class="crumb crumb-{parity}">'.format(parity=parity) + html.escape(crumb, quote=False) + '</span>')

      breadcrumbs_string = get_separator(self.view).join(breadcrumbs)
      body = template.format(
          breadcrumbs=''.join(crumb_elements),
          stylesheet=stylesheet
      )
      phantom = sublime.Phantom(
          region,
          body,
          sublime.LAYOUT_BLOCK,
          on_navigate=lambda href, breadcrumbs_string=breadcrumbs_string: self.navigate(href, breadcrumbs_string)
      )
      phantoms.append(phantom)

    self.phantom_set.update(phantoms)
    self.phantoms_visible = True

  def is_visible(self):
    return int(sublime.version()) > 3124
