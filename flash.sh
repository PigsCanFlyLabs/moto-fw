#!/bin/bash

source common.sh

source "${venv_dir}/bin/activate"
pushd "${build_dir}/microPython/project/micropython/ports/esp32"

if [ ! -f "${PORT}" ]; then
  PORT=${PORT:-${1:-/dev/ttyUSB0}}
  if [ ! -f "${PORT}" ]; then
    PORT=/dev/ttyACM0
  fi
fi
BOARD=${BOARD:-${2:-"MOTOC3"}}
BAUD=${BAUD:-9600} # 460800

~/.espressif/python_env/idf4.4_py3.8_env/bin/python ../../../../../esp-idf/components/esptool_py/esptool/esptool.py -p "${PORT}" -b "${BAUD}" --before default_reset --after hard_reset --chip esp32c3  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 "build-${BOARD}/bootloader/bootloader.bin" 0x8000 "build-${BOARD}/partition_table/partition-table.bin" 0x10000 "build-${BOARD}/micropython.bin"
