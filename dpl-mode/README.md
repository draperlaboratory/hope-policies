# Policy Language Emacs Mode

This directory contains a dirt-simple emacs mode for the policy
language.  It current just does very basic syntax highlighting - no
indenting or special commands.

## Installation

Put dpl-mode.el somewhere.  Let's say `~/usr/share/emacs/site-lisp`.
Make sure that directory is on your loadpath.  If you're not sure, add
something like this to your `.emacs` file:

    (setq load-path (cons (expand-file-name "~/usr/share/emacs/site-lisp") 
                          load-path))

Then tell emacs to use this mode when it opens a `.dpl` file, by
adding these lines to your `.emacs` file:

    (require 'dpl-mode)
    (add-to-list 'auto-mode-alist '("\\.dpl\\'" . dpl-mode))

## Known flaws

The emacs mode just has a built-in list of the identifiers used in
rules to select a piece of metadata ("mem", "env", "op1", etc.).  If
you define a new one in a opgroup, it won't get colored correctly.
The right fix is probably to use a regexp to pull apart rules and
color their bits individually.

No coloring for opgroup definitions, or for the indivdual tag
patterns/tag expressions.
