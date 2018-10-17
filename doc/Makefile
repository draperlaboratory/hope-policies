SRC_ORG_FILES=$(wildcard *.org)
TARGET_MD_FILES=$(patsubst %.org,%.md,$(SRC_ORG_FILES))
OUT_DIR=out-markdown

vpath $(OUT_DIR)

.PHONY: all
all: $(TARGET_MD_FILES)

.PHONY: clean
clean:
	-rm -rf -- $(OUT_DIR)

%.md: %.org
	mkdir -p -- $(OUT_DIR)
	emacs $< --batch --eval '(progn (org-md-export-to-markdown) (rename-file "$@" "$(OUT_DIR)/$@"))' --kill
