#!/bin/sh
# Aponta o git deste clone para .githooks/. Roda uma vez por máquina.
set -e
cd "$(dirname "$0")/.."
git config core.hooksPath .githooks
chmod +x .githooks/*
echo "hooks instalados: core.hooksPath = .githooks"
echo "conferir: git config core.hooksPath"
