(defvar dpl-mode-syntax-table nil "Syntax table for `dpl-mode'.")

;; This adds 
(setq dpl-mode-syntax-table
      (let ( (synTable (make-syntax-table)))
        ;; comment style “/* … */”
        (modify-syntax-entry ?\/ ". 124" synTable)
        (modify-syntax-entry ?* ". 23b" synTable)
        (modify-syntax-entry ?\n ">" synTable)
        synTable))

(setq dpl-font-lock-keywords
      (let* (
            ;; define several category of keywords
            (x-keywords '("module" "import" "group" "metadata" "policy" "require" "type" "data"))
            (x-constants '("code" "mem" "env" "op1" "op2" "res" "target" "addr" "val" "return" "csr"))
            (x-functions '("init" "grp"))

            (x-keywords-regexp (regexp-opt x-keywords 'words))
            (x-constants-regexp (regexp-opt x-constants 'words))
            (x-functions-regexp (regexp-opt x-functions 'words))
            )

        `(
          (,x-constants-regexp . font-lock-type-face)
          (,x-functions-regexp . font-lock-function-name-face)
          (,x-keywords-regexp . font-lock-keyword-face)
          ("->\\|[-\\+:=\\^,]" . font-lock-variable-name-face)
          ;; note: order above matters, because once colored, that part won't change.
          ;; in general, put longer words first
          )))

(define-derived-mode dpl-mode prog-mode "dpl"
  "dpl-mode is a major mode for editing micropolicies."
  (setq font-lock-defaults `((dpl-font-lock-keywords))))

(provide 'dpl-mode)
