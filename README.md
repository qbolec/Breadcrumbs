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

The settings include values to limit the length of breadcrumbs and you can create your own regular expressions so it includes only what you need. Settings can be further customized [per syntax](https://www.sublimetext.com/docs/3/settings.html).

Open Preferences > Package Settings > Breadcrumbs > Settings to view all options. 

### Example key bindings

This package doesn't provide key bindings for its commands, allowing you to customize them as you see fit. Here are some examples:

```json
{ "keys": ["super+ctrl+b"], "command": "breadcrumbs_popup" },
{ "keys": ["super+ctrl+alt+b"], "command": "breadcrumbs_phantom" }
```
