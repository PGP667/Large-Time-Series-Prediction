#!/usr/bin/env bash
set -euo pipefail
# Making prediction using LSTM model
SPARK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPARK_MASTER="${SPARK_MASTER:-local[*]}"
SPARK_DEPLOY_MODE="${SPARK_DEPLOY_MODE:-client}"
SPARK_SUBMIT="${SPARK_SUBMIT:-spark-submit}"
export PYSPARK_PYTHON="${PYSPARK_PYTHON:-python3}"
export PYSPARK_DRIVER_PYTHON="${PYSPARK_DRIVER_PYTHON:-$PYSPARK_PYTHON}"

cd "$SPARK_DIR"
"$SPARK_SUBMIT" \
            --master "$SPARK_MASTER" \
            --deploy-mode "$SPARK_DEPLOY_MODE" \
            --py-files tools.zip \
            src/prediction/lstm.py "$1"
