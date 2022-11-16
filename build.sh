#!/bin/bash

source common.sh

MICRO_PYTHON_VERSION=${MICRO_PYTHON_VERSION:-master}
ESP_IDF_VERSION="v4.4.3"
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

mkdir -p ./microPython/project
pushd ./microPython/project

pwd
if [ ! -d "micropython" ]; then
  git clone -b "${MICRO_PYTHON_VERSION}" --recurse-submodules https://github.com/micropython/micropython.git &> clone_logs || (cat clone_logs; exit 1)
fi
pushd micropython
MP_ROOT=$(pwd)

git fetch || echo "No internet, not updating."
git checkout
git checkout "${MICRO_PYTHON_VERSION}"

if [ ! -f "${build_dir}/microPython/project/micropython/mpy-cross/mpy-cross" ]; then
  pushd mpy-cross
  make
  if [ -f mpy-cross ]; then
    cp mpy-cross "${venv_dir}/bin/"
  elif [ -f build/mpy-cross ]; then
    cp build/mpy-cross "${venv_dir}/bin/"
  else
    echo "Could not find mpy cross?"
    exit 1
  fi
  popd
fi
pushd ./ports/unix
if ! command -v micropython &> /dev/null; then
  if [ ! -f "micorpython" ]; then
    if [ ! -f "./build-standard/micorpython" ]; then
      make submodules &> submod
      make &> base || (cat base; exit 1)
    fi
  fi
  export PATH="${PATH}:$(pwd):$(pwd)/build-standard/"
fi
popd
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
pushd "${MP_ROOT}/ports/esp32"
if [ ! -d "esp-idf" ]; then
  ln -s "${build_dir}/esp-idf" ./esp-idf
fi
cp -af "${BOARD_DIR}/"* ./boards || echo "already copied"
make submodules &> submod
# make BOARD=GENERIC &> base
make -j36 BOARD=${BOARD:-MOTOC3} FROZEN_MANIFEST="${SCRIPT_DIR}/fw/manifest.py" clean
make V=2 -j36 BOARD=${BOARD:-MOTOC3} FROZEN_MANIFEST="${SCRIPT_DIR}/fw/manifest.py"
# make BOARD=${BOARD:-MOTOC3}
# USER_C_MODULES="${SCRIPT_DIR}/modules/micropython.cmake"
pwd
popd

