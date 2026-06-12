
import warnings
warnings.filterwarnings ("ignore", message="numpy.dtype size changed")
warnings.filterwarnings ("ignore", message="numpy.ufunc size changed")

from pyspark import SparkContext
from pyspark import SQLContext
from pyspark import SparkConf
from pyspark.sql.functions import *

import sys
import subprocess
import os
from pathlib import Path

conf = (SparkConf ())
sc = SparkContext (conf = conf)
sqlcontext =  SQLContext(sc)

def local_to_hdfs (data_path):
    local_path = Path(data_path).expanduser()
    hdfs_input_dir = os.environ.get("LTSP_HDFS_INPUT_DIR", f"/user/{os.environ.get('USER', 'hduser')}")

    try:
        subprocess.run(["hdfs", "dfs", "-mkdir", "-p", hdfs_input_dir], check=True)
        subprocess.run(["hdfs", "dfs", "-put", "-f", data_path, hdfs_input_dir + "/"], check=True)
    except subprocess.CalledProcessError as exc:
        print(exc)
    data_name = local_path.stem
    csv_uri = local_path.resolve().as_uri() if local_path.exists() else data_path
    df = sqlcontext.read.load (csv_uri,
                        format='csv',  
                        header='true',
                        inferSchema='true',
                        inferschema='true',
                        comment = '#',
                        sep = ';')
                           
    cols = df.columns[1:]
      
    rdd = sc.parallelize ((cols. index (cols[i]), cols[i], df.select (cols[i]). toPandas() [cols[i]]. tolist ()) for i in range (len (cols)))
    rdd. toDF (["id", "colname", "time_series"]). show ()
    output_dir = os.environ.get("LTSP_HDFS_DATA_DIR", "/user/hduser/data")
    rdd. toDF (["id", "colname", "time_series"]). write. parquet (output_dir + "/" + data_name, mode='overwrite')

if __name__ == "__main__":

    input_data = sys.argv[1]
    local_to_hdfs (input_data)
