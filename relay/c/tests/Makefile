.PHONY: all test clean

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g -I../include
LDFLAGS =

SRC_DIR = ../src
BUILD_DIR = build

# Source files for library (excluding main.c)
LIB_SOURCES = $(SRC_DIR)/avro_writer.c \
              $(SRC_DIR)/decimator.c \
              $(SRC_DIR)/sockets.c \
              $(SRC_DIR)/config.c \
              $(SRC_DIR)/utils.c

LIB_OBJECTS = $(LIB_SOURCES:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)

# Test executables
TESTS = $(BUILD_DIR)/test_utils \
        $(BUILD_DIR)/test_decimator \
        $(BUILD_DIR)/test_avro_writer

all: $(BUILD_DIR) $(TESTS)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Compile library objects
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

# Build test executables
$(BUILD_DIR)/test_utils: test_utils.c $(BUILD_DIR)/utils.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BUILD_DIR)/test_decimator: test_decimator.c $(BUILD_DIR)/decimator.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BUILD_DIR)/test_avro_writer: test_avro_writer.c $(BUILD_DIR)/avro_writer.o $(BUILD_DIR)/utils.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Run all tests
test: all
	@echo "=== Running Unit Tests ==="
	@$(BUILD_DIR)/test_utils
	@echo ""
	@$(BUILD_DIR)/test_decimator
	@echo ""
	@$(BUILD_DIR)/test_avro_writer
	@echo ""
	@echo "=== All Unit Tests Passed ==="

clean:
	rm -rf $(BUILD_DIR)
