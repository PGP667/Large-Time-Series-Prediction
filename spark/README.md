# Spark/HDFS

Cette partie contient la version distribuee du pipeline Large Time Series Prediction.

Elle utilise PySpark pour transformer les donnees, calculer des graphes, lancer la selection PEHAR distribuee et executer la prediction LSTM distribuee.

## Structure

```text
spark/
|-- data/                # Donnees d'exemple
|-- jobs/                # Wrappers spark-submit
|-- src/
|   |-- local_to_hdfs/   # Conversion CSV local -> parquet HDFS
|   |-- compute_graphs/  # Calcul des graphes
|   |-- data_preparation/# SVD / preparation distribuee
|   |-- feature_selection/# Selection PEHAR distribuee
|   `-- prediction/      # Prediction LSTM Spark
|-- tools/               # Modules Python Spark
`-- tools.zip            # Package transmis a spark-submit
```

## Configuration

Les scripts dans `spark/jobs/` acceptent les variables suivantes :

| Variable | Defaut | Description |
| --- | --- | --- |
| `SPARK_MASTER` | `local[*]` | Master Spark, par exemple `local[*]` ou `yarn` |
| `SPARK_DEPLOY_MODE` | `client` | Mode de deploiement Spark |
| `SPARK_SUBMIT` | `spark-submit` | Binaire `spark-submit` a utiliser |
| `PYSPARK_PYTHON` | `python3` | Python des executors |
| `PYSPARK_DRIVER_PYTHON` | valeur de `PYSPARK_PYTHON` | Python du driver |
| `LTSP_HDFS_INPUT_DIR` | `/user/<USER>` | Dossier HDFS pour copier les CSV d'entree |
| `LTSP_HDFS_DATA_DIR` | `/user/hduser/data` | Dossier HDFS pour les donnees parquet |

Configuration locale recommandee :

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export SPARK_MASTER="local[*]"
export SPARK_DEPLOY_MODE="client"
export SPARK_SUBMIT="$PWD/.venv311/bin/spark-submit"
export PYSPARK_PYTHON="$PWD/.venv311/bin/python"
export PYSPARK_DRIVER_PYTHON="$PYSPARK_PYTHON"
```

Pour un cluster YARN :

```bash
export SPARK_MASTER="yarn"
export SPARK_DEPLOY_MODE="client"
```

## Jobs disponibles

### 1. Copier et convertir les donnees

```bash
bash spark/jobs/local_to_distributed.sh /absolute/path/to/data.csv
```

Ce job :

1. copie le CSV dans HDFS ;
2. lit le CSV local avec Spark ;
3. convertit les colonnes en series temporelles ;
4. ecrit un parquet dans `LTSP_HDFS_DATA_DIR`.

### 2. Calculer le graphe de causalite

```bash
bash spark/jobs/causality_mat.sh hdfs:///path/to/parquet
```

### 3. Preparer les donnees

```bash
bash spark/jobs/data_preparation.sh hdfs:///path/to/parquet
```

### 4. Selection PEHAR distribuee

```bash
bash spark/jobs/pehar_dist.sh hdfs:///path/to/parquet
```

### 5. Prediction LSTM distribuee

```bash
bash spark/jobs/prediction.sh hdfs:///path/to/parquet
```

## Smoke test local

Verifier Spark :

```bash
SPARK_LOCAL_IP=127.0.0.1 python - <<'PY'
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[1]").appName("ltsp-smoke").getOrCreate()
print(spark.range(3).count())
spark.stop()
PY
```

Verifier HDFS :

```bash
hdfs dfs -mkdir -p /tmp/ltsp-test
hdfs dfs -put -f spark/data/ausmacro.csv /tmp/ltsp-test/ausmacro.csv
hdfs dfs -ls /tmp/ltsp-test
```

Verifier le wrapper du projet :

```bash
export LTSP_HDFS_DATA_DIR="/tmp/ltsp-test/data"
bash spark/jobs/local_to_distributed.sh "$PWD/spark/data/ausmacro.csv"
hdfs dfs -ls /tmp/ltsp-test/data/ausmacro
```

La sortie doit contenir `_SUCCESS` et des fichiers `.parquet`.

## Notes

- `tools.zip` doit rester present : il est transmis a Spark via `--py-files`.
- Les scripts sont executables, mais `bash spark/jobs/<job>.sh ...` reste portable.
- Les chemins HDFS peuvent etre adaptes avec `LTSP_HDFS_INPUT_DIR` et `LTSP_HDFS_DATA_DIR`.
- Les avertissements Hadoop sur les librairies natives ne sont pas bloquants sur une installation locale.
