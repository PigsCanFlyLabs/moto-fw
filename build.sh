#!/bin/bash

source common.sh

MICRO_PYTHON_VERSION=${MICRO_PYTHON_VERSION:-main}
ESP_IDF_VERSION="v4.4.2"
if [ ! -d "${build_dir}" ]; then
  mkdir "${build_dir}"
fi
pushd "${build_dir}"

if [ ! -d "${venv_dir}" ]; then
  virtualenv  "${venv_dir}"
fi

# Install the esp-idf dev tool chain if needed
# Note: can not be called from inside a venv
if ! command -v idf.py &> /dev/null; then
  if [ ! -d "esp-idf" ]; then
    git clone -b "${ESP_IDF_VERSION}" --recursive https://github.com/espressif/esp-idf.git &> clone_logs || (cat clone_logs; exit 1)
  fi
  pushd esp-idf
  if [ ! -d "~/.espressif" ]; then
    (./install.sh &> espidf_install) || (cat espidf_install; exit 1)
  fi
  source ./export.sh
  popd
fi

mkdir -p ./circuitpython/project
pushd ./circuitpython/project

pwd
if [ ! -d "circuitpython" ]; then
  git clone -b "${MICRO_PYTHON_VERSION}" --recurse-submodules git@github.com:adafruit/circuitpython.git &> clone_logs || (cat clone_logs; exit 1)
fi
pushd circuitpython
MP_ROOT=$(pwd)

git fetch || echo "No internet, not updating."
git checkout
git checkout "${MICRO_PYTHON_VERSION}"

pip install -r requirements-dev.txt
make -C mpy-cross

if ! command -v minipip &> /dev/null; then
  pip install minipip
fi

pushd ./ports/unix
if ! command -v micropython &> /dev/null; then
  if [ ! -f "micropython" ]; then
    make submodules &> submod
    make &> base || (cat base; exit 1)
  fi
  export PATH="${PATH}:$(pwd):$(pwd)/build-standard/"
fi
popd
# Make uasyncio available for testing on unix port
if [ ! -d ~/.micropython/lib/ ]; then
  mkdir -p ~/.micropython/lib
  cp -af ./extmod/* ~/.micropython/lib/
  micropython -m upip install unittest logging threading typing warnings base64 hmac  
fi
# Run some smoke tests
pushd "${FW_DIR}"
# flake8 --max-line-length 100 --ignore=Q000 --ignore=W504 --exclude=manifest.py
micropython -c "import unittest;unittest.main('smoke_test')"
popd
pushd "${MP_ROOT}/ports/esp32"
if [ ! -d "esp-idf" ]; then
  ln -s "${build_dir}/esp-idf" ./esp-idf
fi
cp -af "${BOARD_DIR}/"* ./boards || echo "already copied"
make submodules &> submod
# make BOARD=GENERIC &> base
make BOARD=${BOARD:-MOTOC3} FROZEN_MANIFEST="${SCRIPT_DIR}/fw/manifest.py" clean
make USER_C_MODULES="${SCRIPT_DIR}/modules/micropython.cmake" clean
make BOARD=${BOARD:-MOTOC3} FROZEN_MANIFEST="${SCRIPT_DIR}/fw/manifest.py"
# make BOARD=${BOARD:-MOTOC3}
# USER_C_MODULES="${SCRIPT_DIR}/modules/micropython.cmake"
pwd
popd

