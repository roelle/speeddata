.PHONY: all clean test

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2 -Iinclude
LDFLAGS =

SRC_DIR = src
TEST_DIR = tests
BUILD_DIR = build
BIN = relay

SOURCES = $(SRC_DIR)/main.c \
          $(SRC_DIR)/avro_writer.c \
          $(SRC_DIR)/decimator.c \
          $(SRC_DIR)/sockets.c \
          $(SRC_DIR)/config.c \
          $(SRC_DIR)/utils.c

OBJECTS = $(SOURCES:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)

# Default target
all: $(BUILD_DIR) $(BUILD_DIR)/$(BIN)

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Link binary
$(BUILD_DIR)/$(BIN): $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
	@echo "Built: $@"

# Compile source files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)
	@echo "Cleaned build directory"

# Run tests (placeholder)
test:
	@echo "Running tests..."
	@cd $(TEST_DIR) && $(MAKE) test

# Install (copy to parent relay directory)
install: all
	cp $(BUILD_DIR)/$(BIN) ../$(BIN)
	@echo "Installed relay binary to ../relay"
