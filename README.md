# Breadcrumbs
A plugin to Sublime Text 2 and Sublime Text 3, which adds breadcrumbs to the status bar based on scopes the current line belongs to. Alternatively, the breadcrumbs can be displayed in a popup using the Show Breadcrumbs command.
This is done based on indentation, by assuming that scopes are indented.

For example if your code looks like this:
```
foo(){
  bar:
    if (whatever){
      cox()
    } else {
      blah->
        zoo
    }
}
```
and the carret is currently in the line with `zoo`, then the breadbrumbs would be:
`foo(){`, `bar:`, `} else {`, and `blah->`.

This approach is quite language agnostic, and I find it mostly usefull for code which spans many lines in which tracking indentation and context is difficult to me (for example in .sass files).

## Instalation

The easiest way is to use [Package Control](https://packagecontrol.io/):

1. press CTRL+SHIFT+P (on Mac: CMD+SHIFT+P)
2. type: "Package Control: Install Package"
3. hit Enter
4. type "Breadcrumbs"
5. hit Enter

## Settings

You can edit Breadcrumbs.sublime-settings to specify the following values:

| name | type | default value | meaning |
|------|------|---------|---------|
|"breadcrumb_length_limit" | Number | 100 | Trim each line to this many characters to form a breadcrumb |
| "total_breadcrumbs_length_limit" | Number | 200 | Make sure that the total length of the status is no longer than this many characters, by trimming the longest breadcrumbs first |
| "breadcrumbs_separator" | String | " › " | Separate breadcrumbs using this character |
| "breadcrumbs_regex" | String | "^\\s*(?P<name>.*\\S)" | Use only the part that matches the "name" group |
| "breadcrumbs_statusbar" | Boolean | true | Optionally disable hide the breadcrumbs from the statusbar |

### Example regexes

To only show Python classes and methods use:  
`"^\\s*(def|class)\\s+(?P<name>.+)\\(.*"`
