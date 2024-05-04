#!/usr/bin/env bash

function create_venv() {
  echo ======== 默认使用工程目录下 venv 文件夹作为虚拟环境，但似乎没有找到此文件夹，是否要安装？ Y 继续 ============
  read input
  if [[ $(echo $input | tr '[a-z]' '[A-Z]') != Y ]]; then
    exit 1
  fi

  if [[ -z $PYTHON_PATH ]]; then
    pys=("python3.8" "python" "python3" "py" "py3")
    for py in ${pys[@]}; do
      hash $py
      if [[ $? -ne 0 ]]; then
        continue
      else
        python_version=($($py -c 'import sys; print(sys.version_info.major, sys.version_info.minor)'))
        if [[ ${python_version[0]} -eq 3 && ${python_version[1]} -ge 7 ]]; then
          PYTHON_PATH=$py
          break
        fi
      fi
    done
  fi

  if [[ -z $PYTHON_PATH ]]; then
    echo "没有有效的解释器！请确保 PATH 中有 Python>=3.7 的解释器，或者手动设置 PYTHON_PATH 到一个解释器的路径上！"
    exit 1
  fi

  echo "===== 找到Python解释器，正在使用 $(which $PYTHON_PATH) 创建虚拟环境 ===="
  $PYTHON_PATH -m venv venv
  echo "============== 创建虚拟环境完成！=================="
  echo " "
  echo " "

  echo "============ 你希望安装本项目的依赖吗？Y 继续 ============"
  read input

  if [[ $(echo $input | tr '[a-z]' '[A-Z]') != Y ]]; then
    echo "你可以自己运行 venv/bin/pip3 install -r requirements.txt 来安装依赖"
    exit 0
  fi

  venv/bin/pip3 install -r requirements.txt
  echo "============ 完成! 为了启用虚拟环境，请运行 source venv/bin/activate ，Windows 的话请使用 WSL/Docker 进行开发！============="
}

if [[ ! -e venv ]]; then
  create_venv
fi
venv/bin/pip3 install -r requirements.txt
