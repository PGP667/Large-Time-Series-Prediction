# Large Time Series Prediction

Framework de prediction pour grandes series temporelles multivariees.

Ce projet implemente un pipeline de recherche compose de cinq etapes :

1. construction de graphes de dependance entre series temporelles ;
2. selection ou reduction du nombre de predicteurs ;
3. prediction avec plusieurs familles de modeles ;
4. calcul des erreurs ;
5. comparaison des methodes et selection des meilleurs couples modele/methode.

Le code historique a ete modernise pour fonctionner avec des versions recentes de Python, R, TensorFlow, Spark et Hadoop tout en gardant la logique originale du travail de these.

## Fonctionnalites

- Graphes de causalite : Granger causality et transfer entropy.
- Selection de variables : PEHAR, FCBF.
- Reduction de dimension : PCA, KernelPCA, FactorAnalysis.
- Modeles de prediction : ARIMA, VECM, LSTM, VAR avec shrinkage.
- Evaluation experimentale complete avec export CSV/XLSX.
- Mode forecast final a partir des meilleurs resultats d'evaluation.
- Version Spark/HDFS pour les traitements distribues.

## Structure

```text
.
|-- data/                    # Jeux de donnees d'exemple pour le pipeline local
|-- src/
|   |-- pre_selection/       # Calcul des graphes de causalite
|   |-- selection/           # Selection de variables et reduction de dimension
|   |-- prediction/          # Modeles de prediction locaux
|   |-- pre_evaluation/      # Calcul des erreurs
|   |-- evaluation/          # Comparaison et synthese des resultats
|   `-- tools/               # Utilitaires partages
|-- spark/
|   |-- data/                # Jeux de donnees Spark d'exemple
|   |-- jobs/                # Wrappers spark-submit
|   |-- src/                 # Jobs PySpark
|   `-- tools/               # Utilitaires Spark packages dans tools.zip
|-- process.py               # Pipeline experimental local
|-- prediction.py            # Mode forecast final
|-- requirements.txt         # Dependances Python
|-- requirements.R           # Dependances R
`-- pyproject.toml           # Configuration projet Python moderne
```

Les resultats generes sont ecrits dans `results/`. Les forecasts finaux sont ecrits dans `Processed/`.

## Prerequis

Versions recommandees :

- Python 3.11 ou 3.12 ;
- R 4.0 ou plus recent ;
- Java 17 pour Spark/Hadoop ;
- Hadoop/HDFS si les jobs Spark doivent etre testes localement ;
- Spark via `pyspark` ou installation systeme.

Sur macOS avec Homebrew :

```bash
brew install r hadoop openjdk@17
```

## Installation

Creer l'environnement Python :

```bash
python3.11 -m venv .venv311
source .venv311/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Installer les dependances R :

```bash
Rscript requirements.R
```

Si Java 17 n'est pas detecte automatiquement :

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
```

## Format des donnees

Le pipeline attend un fichier CSV separe par des points-virgules. Les premieres lignes peuvent contenir des metadonnees sous forme de commentaires commencant par `#`.

Exemple minimal :

```text
# name_prefix: example
# lag_parameter: 2
# predict: Y1,Y2
# number_predictions: 12
# horizon: 1
# prediction_type: cross-validation
# max_attributes: 3
Date;Y1;Y2;X1;X2
2000-01;1.0;2.0;0.5;0.7
2000-02;1.1;2.1;0.6;0.8
```

Metadonnees importantes :

- `name_prefix` : nom logique du jeu de donnees ;
- `description` : description optionnelle ;
- `lag_parameter` : nombre de retards utilises ;
- `predict` : variables cibles a predire ;
- `number_predictions` : taille du jeu de test ;
- `horizon` : horizon de prediction ;
- `prediction_type` : `cross-validation` ou `rolling` ;
- `max_attributes` : nombre maximal de variables selectionnees.

Des exemples sont disponibles dans `data/`.

## Pipeline experimental local

Le pipeline local est pilote par `process.py`.

Ordre recommande :

```bash
python process.py data/us_diff.csv -t pre_selection
python process.py data/us_diff.csv -t selection
python process.py data/us_diff.csv -t prediction
python process.py data/us_diff.csv -t pre_evaluation
python process.py data/us_diff.csv -t evaluation
```

Etapes disponibles :

| Etape | Alias | Role |
| --- | --- | --- |
| `pre_selection` | `ps` | Calcule les graphes de causalite |
| `selection` | `s` | Calcule les selections/reductions de predicteurs |
| `prediction` | `p` | Lance les modeles de prediction |
| `pre_evaluation` | `pe` | Calcule les erreurs par methode |
| `evaluation` | `e` | Produit les tableaux comparatifs finaux |

Lancer une seule methode :

```bash
python process.py data/us_diff.csv -t selection -s src/selection/pehar_fselection.py
python process.py data/us_diff.csv -t prediction -s src/prediction/auto_arima.py
```

Par defaut, l'etape `prediction` lance les modeles suivants :

- `var_shrinkage.py`
- `auto_arima.py`
- `lstm.py`
- `vecm.py`

## Forecast final

`prediction.py` sert a produire des predictions finales dans `Processed/<dataset>/`.

Mode `eval` : reutilise les meilleurs modeles trouves par l'evaluation.

```bash
python prediction.py -d data/us_diff.csv -m eval
```

Mode `direct` : impose le modele, la methode de selection et le nombre de predicteurs.

```bash
python prediction.py \
  -d data/us_diff.csv \
  -m direct \
  -pr ARIMA \
  -fsm PEHAR_gc \
  -nbp 2 \
  -g gc
```

Arguments principaux :

| Argument | Description |
| --- | --- |
| `-d`, `--data` | Fichier CSV a traiter |
| `-m`, `--mode` | `eval` ou `direct` |
| `-pr`, `--pred_model` | `ARIMA` ou `VECM` |
| `-fsm`, `--fs_method` | `PEHAR_gc` ou `PEHAR_te` |
| `-nbp`, `--nb_predictors` | Nombre de predicteurs a selectionner |
| `-g`, `--graph_type` | `gc` pour Granger, `te` pour transfer entropy |

## Version Spark/HDFS

La partie Spark est documentee dans [spark/README.md](spark/README.md).

Les scripts `spark/jobs/*.sh` sont configurables avec des variables d'environnement :

```bash
export SPARK_MASTER="local[*]"
export SPARK_DEPLOY_MODE="client"
export SPARK_SUBMIT=".venv311/bin/spark-submit"
export PYSPARK_PYTHON="$PWD/.venv311/bin/python"
export PYSPARK_DRIVER_PYTHON="$PYSPARK_PYTHON"
```

Exemple :

```bash
bash spark/jobs/local_to_distributed.sh /absolute/path/to/data.csv
```

Pour utiliser un cluster YARN :

```bash
SPARK_MASTER=yarn bash spark/jobs/local_to_distributed.sh /absolute/path/to/data.csv
```

## Tests et validation

Voir [docs/VALIDATION.md](docs/VALIDATION.md) pour les commandes de smoke test recommandees.

Commandes rapides :

```bash
python -m compileall -q prediction.py process.py src spark/src spark/tools
python process.py data/us_diff.csv -t pre_selection
python process.py data/us_diff.csv -t selection
python process.py data/us_diff.csv -t prediction
python process.py data/us_diff.csv -t pre_evaluation
python process.py data/us_diff.csv -t evaluation
```

Pour limiter le parallelisme sur une machine locale :

```bash
export LTSP_N_JOBS=1
```

## Sorties

Arborescence typique :

```text
results/
|-- pre_selection/<dataset>/      # Graphes de causalite
|-- selection/<dataset>/          # Predicteurs selectionnes
|-- prediction/<dataset>/         # Predictions par modele/methode
|-- pre_evaluation/<dataset>/     # Erreurs intermediaires
`-- evaluation/<dataset>/         # Syntheses XLSX

Processed/
`-- <dataset>/
    |-- predictions.csv
    |-- info_models.csv
    `-- causality_graph_gc.csv
```

## Notes de maintenance

- Le code conserve volontairement l'architecture historique du projet pour rester proche de la logique de these.
- Les traitements LSTM peuvent etre plus lents que les autres modeles.
- Certains avertissements TensorFlow, Matplotlib ou Hadoop peuvent apparaitre selon la machine ; ils ne sont pas bloquants si les commandes se terminent avec un code 0.
- Les gros resultats experimentaux ne doivent pas etre versionnes dans un nouveau travail ; regenerer `results/` quand c'est possible.

## Etat actuel

Le projet a ete valide localement avec :

- Python 3.11 ;
- R 4.6 ;
- TensorFlow 2.x via `tensorflow.keras` ;
- PySpark ;
- Hadoop/HDFS local ;
- pipeline experimental complet sur jeu de donnees de smoke test ;
- lecture/ecriture Spark vers HDFS.
