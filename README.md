# Breadcrumbs
A Sublime 2 Plugin which adds breadcrumbs to the status bar based on scopes the current line belongs to.
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
```
foo(){ ■ bar:  ■ } else { ■ blah-> ■
```

This approach is quite language agnostic, and I find it mostly usefull for code which spans many lines in which tracking indentation and context is difficult to me (for example in .sass files).


## Settings

You can edit Breadcrumbs.sublime-settings to specify following values:
|| name || default value || meaning ||
|"breadcrumb_length_limit" | 100 | Trim each line to this many characters to form a breadcrumb |
| "total_breadcrumbs_length_limit" | 200 | Make sure that the total length of the status is no longer than this many characters, by trimming the longest breadcrumbs first |
| "breadcrumbs_separator" | " ■ " | Separate breadcrumbs using this character |
