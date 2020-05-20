RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST=password/webapp_password_leak
TEST_SOURCE=test.c
TEST_ROOT_DIR=$(realpath ..)

include test.mk
include ../webapp/common.mk