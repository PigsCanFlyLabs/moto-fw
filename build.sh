#!/bin/bash

source common.sh

MICRO_PYTHON_VERSION=${MICRO_PYTHON_VERSION:-main}
ESP_IDF_VERSION="v4.4.2"
if [ ! -d "${build_dir}" ]; then
  mkdir "${build_dir}"
fi
pushd "${build_dir}"

if ! command -v ninja &> /dev/null; then
  sudo apt-get install -y ninja-build
fi

# Grab unittest from micropython yeeeah...
if [ ! -f "circuitpython/project/circuitpython/lib/unittest.py" ]; then
  cp -af ~/.micropython/lib/* circuitpython/project/circuitpython/lib/
fi

if [ ! -d "${venv_dir}" ]; then
  virtualenv  "${venv_dir}"
fi

# Install the esp-idf dev tool chain if needed
# Note: can not be called from inside a venv
if ! command -v idf.py &> /dev/null; then
  if [ ! -d "esp-idf" ]; then
    git clone -b "${ESP_IDF_VERSION}" --recursive https://github.com/espressif/esp-idf.git &> clone_logs || (cat clone_logs; exit 1)
    git submodule update --init --recursive
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
  git clone -b "${MICRO_PYTHON_VERSION}" --recurse-submodules git@github.com:holdenk/circuitpython.git &> clone_logs || (cat clone_logs; exit 1)
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

if ! command -v micropython &> /dev/null; then
  make -C mpy-cross
  pushd ./ports/unix
  export PATH="${PATH}:$(pwd):$(pwd)/build-standard/"
  popd
fi
# Make uasyncio available for testing on unix port
if [ ! -d ~/.micropython/lib/ ]; then
  mkdir -p ~/.micropython/lib
  cp -af ./extmod/* ~/.micropython/lib/
  # TODO: switch to mip once it works.
  micropython -m upip install unittest logging threading typing warnings base64 hmac  
fi
# Run some smoke tests
pushd "${FW_DIR}"
# flake8 --max-line-length 100 --ignore=Q000 --ignore=W504 --exclude=manifest.py
micropython -c "import unittest;unittest.main('smoke_test')"
popd
pushd "${MP_ROOT}/ports/espressif"
rm -rf esp-idf
ln -s "${build_dir}/esp-idf" ./esp-idf
cp -af "${BOARD_DIR}/"* ./boards || echo "already copied"
make BOARD=${BOARD:-MOTOC3} FROZEN_MANIFEST="${SCRIPT_DIR}/fw/manifest.py" clean
# Only _partail_ support for FROZEN_MANIFEST in circuitpython :'(
make V=2 BOARD=${BOARD:-MOTOC3} FROZEN_MPY_PY_FILES="${SCRIPT_DIR}/fw/main.py"
make flash BOARD=MOTOC3 PORT=/dev/ttyACM0
# make BOARD=${BOARD:-MOTOC3}
# USER_C_MODULES="${SCRIPT_DIR}/modules/micropython.cmake"
pwd
popd

