#!/bin/bash

source common.sh

source "${venv_dir}/bin/activate"
pushd "${build_dir}/microPython/project/micropython/ports/esp32"

if [ ! -f "${PORT}" ]; then
  PORT=${PORT:-${1:-/dev/ttyUSB0}}
  if [ ! -f "${PORT}" ]; then
    PORT=$(ls -1 /dev/ttyACM* | head -n 1)
  fi
fi
BOARD=${BOARD:-${2:-"MOTOC3"}}
BAUD=${BAUD:-115200} #460800} #9600} # 460800
FLASH_MODE=${FLASH_MODE:-dio} # On low poer device use dout

function flash () {
  ~/.espressif/python_env/idf4.4_py3.8_env/bin/python \
    ../../../../../esp-idf/components/esptool_py/esptool/esptool.py \
    ${EXTRA} -p "${PORT}" -b "${BAUD}" --before default_reset \
    --after hard_reset --chip esp32c3  write_flash --flash_mode "${FLASH_MODE}" \
    --flash_size detect --flash_freq 40m 0x0 \
    "build-${BOARD}/bootloader/bootloader.bin" 0x8000 \
    "build-${BOARD}/partition_table/partition-table.bin" 0x10000 \
    "build-${BOARD}/micropython.bin"
}

flash || EXTRA="--no-stub" flash
