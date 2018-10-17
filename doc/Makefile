#
# This Makefile compiles documents from Emacs Org files to Markdown.
#

OUT_DIR=out-markdown
SRC_ORG_FILES=$(wildcard *.org)
TARGET_MD_FILES=$(patsubst %.org,$(OUT_DIR)/%.md,$(SRC_ORG_FILES))

vpath $(OUT_DIR)

.PHONY: all
all: $(TARGET_MD_FILES)

.PHONY: clean
clean:
	-rm -rf -- $(OUT_DIR)

$(OUT_DIR)/%.md: %.org
	mkdir -p -- $(OUT_DIR)
	emacs $< --batch --eval '(org-md-export-to-markdown)' --kill
	mv -- $(notdir $@) $@
