CC = arm-none-eabi-gcc
GDB = arm-none-eabi-gdb
INC = inc
SRC = src
DEST = dest
LINKER = util/STM32F091RCTx_FLASH.ld
OOCD_SCR = /usr/share/openocd/scripts

INCLUDES = -I$(INC) -I$(INC)/CMSIS
COMMON_FLAGS = -std=c99 -mcpu=cortex-m0 -mlittle-endian -mthumb -DSTM32F091xC
COMP_FLAGS = $(COMMON_FLAGS) -g3 -O0 -Wall -Wextra $(INCLUDES) -c
LINK_FLAGS = $(COMMON_FLAGS) -T$(LINKER) -Wl,--gc-sections --specs=nosys.specs

SRCS = $(wildcard $(SRC)/*.c)
OBJS = $(patsubst $(SRC)/%.c, $(DEST)/%.o, $(SRCS))
DEPS = $(INC)/*.h $(INC)/CMSIS/*.h
STARTUP_SRC = $(SRC)/startup_stm32f091xc.s
STARTUP_OBJ = $(DEST)/startup_stm32f091xc.o

$(DEST)/main.hex: $(DEST)/main.elf
	objcopy -Oihex $(DEST)/main.elf $(DEST)/main.hex

$(DEST)/main.elf: $(OBJS) $(STARTUP_OBJ)
	$(CC) $(LINK_FLAGS) $^ -o $@

$(STARTUP_OBJ): $(STARTUP_SRC)
	$(CC) $(COMP_FLAGS) $< -o $@

$(OBJS): $(DEST)/%.o : $(SRC)/%.c $(DEPS)
	$(CC) $(COMP_FLAGS) $< -o $@

.PHONY: con debug flash clean

con:
	openocd -s $(OOCD_SCR) -f $(OOCD_SCR)/board/st_nucleo_f0.cfg

debug:
	$(GDB) -x util/debug.gdb

flash:
	$(GDB) -x util/flash.gdb

clean:
	rm -f $(DEST)/*.o
