# Validation et smoke tests

Ce document decrit les tests minimaux a lancer apres installation ou modification du projet.

## 1. Activer l'environnement

```bash
source .venv311/bin/activate
export LTSP_N_JOBS=1
```

Sur macOS avec OpenJDK installe par Homebrew :

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
```

## 2. Verifier les dependances

```bash
python - <<'PY'
import numpy
import pandas
import scipy
import sklearn
import statsmodels
import pmdarima
import tensorflow
import pyspark
import openpyxl
import xlrd

print("Python dependencies OK")
PY
```

```bash
Rscript requirements.R
Rscript --version
```

## 3. Verifier la syntaxe Python

```bash
python -m compileall -q prediction.py process.py src spark/src spark/tools
```

## 4. Smoke test local complet

Utiliser un petit CSV au format du projet. Les jeux `data/us_diff.csv` ou `data/us_norm.csv` peuvent servir de base.

```bash
python process.py data/us_diff.csv -t pre_selection
python process.py data/us_diff.csv -t selection
python process.py data/us_diff.csv -t prediction
python process.py data/us_diff.csv -t pre_evaluation
python process.py data/us_diff.csv -t evaluation
```

Sorties attendues :

```text
results/pre_selection/us_diff/
results/selection/us_diff/
results/prediction/us_diff/
results/pre_evaluation/us_diff/
results/evaluation/us_diff/
```

## 5. Forecast final

Apres l'etape `evaluation` :

```bash
python prediction.py -d data/us_diff.csv -m eval
```

Mode direct :

```bash
python prediction.py \
  -d data/us_diff.csv \
  -m direct \
  -pr ARIMA \
  -fsm PEHAR_gc \
  -nbp 2 \
  -g gc
```

Sorties attendues :

```text
Processed/us_diff/predictions.csv
Processed/us_diff/info_models.csv
Processed/us_diff/causality_graph_gc.csv
```

## 6. Tests R directs

```bash
Rscript src/pre_selection/te.R data/us_diff.csv /tmp/ltsp_te
Rscript src/pre_selection/nlin_causality.R data/us_diff.csv /tmp/ltsp_nlin
```

## 7. Smoke test Spark local

Verifier que Spark demarre :

```bash
SPARK_LOCAL_IP=127.0.0.1 python - <<'PY'
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[1]").appName("ltsp-smoke").getOrCreate()
print(spark.range(3).count())
spark.stop()
PY
```

La commande doit afficher `3`.

## 8. Smoke test HDFS/Spark

Ce test suppose qu'un NameNode et un DataNode HDFS sont demarres et que `HADOOP_CONF_DIR` pointe vers leur configuration.

```bash
hdfs dfs -mkdir -p /tmp/ltsp-test
hdfs dfs -put -f data/us_diff.csv /tmp/ltsp-test/us_diff.csv
hdfs dfs -ls /tmp/ltsp-test
```

Lecture/ecriture Spark vers HDFS :

```bash
SPARK_LOCAL_IP=127.0.0.1 python - <<'PY'
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .master("local[1]")
    .appName("ltsp-hdfs-smoke")
    .getOrCreate()
)
spark.range(5).write.mode("overwrite").parquet("hdfs:///tmp/ltsp-test/spark-parquet")
print(spark.read.parquet("hdfs:///tmp/ltsp-test/spark-parquet").count())
spark.stop()
PY
```

La commande doit afficher `5`.

## 9. Job Spark du projet

```bash
export SPARK_MASTER="local[*]"
export SPARK_DEPLOY_MODE="client"
export SPARK_SUBMIT="$PWD/.venv311/bin/spark-submit"
export PYSPARK_PYTHON="$PWD/.venv311/bin/python"
export PYSPARK_DRIVER_PYTHON="$PYSPARK_PYTHON"
export LTSP_HDFS_DATA_DIR="/tmp/ltsp-test/data"

bash spark/jobs/local_to_distributed.sh "$PWD/data/us_diff.csv"
hdfs dfs -ls /tmp/ltsp-test/data/us_diff
```

Une sortie `_SUCCESS` et des fichiers `.parquet` doivent etre presents.

## Avertissements non bloquants connus

- TensorFlow peut afficher des avertissements CPU sur Apple Silicon.
- Matplotlib peut creer un cache temporaire si le dossier utilisateur n'est pas accessible.
- Hadoop peut indiquer que la librairie native n'est pas chargee et utiliser les classes Java integrees.

Ces messages ne sont pas bloquants tant que les commandes sortent avec un code 0 et produisent les fichiers attendus.
