# Breadcrumbs
A plugin for Sublime Text 2 and 3, which shows the breadcrumbs to your current caret position based on indentation.
Breadcrumbs can be displayed in the statusbar, a popup (via Show Breadcrumbs) or in between the lines of your code (via Show Breadcrumbs Inline).

For example if your code looks like this:

```javascript
foo(){
  bar:
    if (whatever){
      cox()
    } else {
      blah ->
        zoo
    }
}
```

With the caret at the line with `zoo`, the breadbrumbs would be:
`foo(){`, `bar:`, `} else {`, and `blah ->`. The "crumbs" can be fine-tuned using a regex.

This approach is language agnostic, can be quite usefull for code that spans many lines and when tracking indentation and context is difficult. It can also help you get your bearings after jumping into a large file (e.g. via search or goto).

## Installation

We recommend using [Package Control](https://packagecontrol.io/):

1. Press CTRL+SHIFT+P (on Mac: CMD+SHIFT+P)
2. Select "Package Control: Install Package"
3. Search for "Breadcrumbs"
4. Hit Enter

## Settings

You can edit Breadcrumbs.sublime-settings to specify the following values:

| name | type | default value | meaning |
|------|------|---------|---------|
|"breadcrumb_length_limit" | Number | 100 | Trim each breadcrumb to this many characters |
| "total_breadcrumbs_length_limit" | Number | 200 | Limit the total length of the breadcrumbs, by trimming the longest breadcrumbs first |
| "breadcrumbs_separator" | String | " › " | Separate breadcrumbs using this string |
| "breadcrumbs_statusbar" | Boolean | true | Optionally hide the breadcrumbs from the statusbar |

### Tuning the breadcrumbs with regular expressions

This packages comes with a very basic regex (`"^\\s*(?P<name>.*\\S)"`) to clean up each breadcrumb. Only the part that matches the "name" group is used.

You can create [Syntax Specific settings](https://www.sublimetext.com/docs/3/settings.html) to fine-tune it for each language you use. Some examples:

- For Python  
`"breadcrumb_regex": "(?i)^\\s*(def|class)\\s*(?P<name>[a-z0-9-_ ]+)\\b"`
- For JSON  
`"breadcrumb_regex": "^\\s*\"(?P<name>[^\"]+)\".*"`

### Example keybindings

This package doesn't provide keybindings for its commands, allowing you to customise them as you see fit. Here are some examples:

```json
{ "keys": ["super+ctrl+b"], "command": "breadcrumbs_popup" },
{ "keys": ["super+ctrl+alt+b"], "command": "breadcrumbs_phantom" }
```
