# Setup file, to execute the whole prediction process or one step.
# Author: Youssef Hmamouche

import argparse
import glob
import shutil
import subprocess
import sys
from pathlib import Path

#==========================================================================#
# Generic funtion to
# Execute one script (python or R) on a file or multiple files in data_path,
# and put results on output_directory
def execute_script (data_path, output_directory, script_path):

	script = Path(script_path)
	script_name = script.name

	if not script.exists():
		print ("Error: the script does not exist!")
		sys.exit(1)

	if script_name.endswith('.py'):
		command = [sys.executable, str(script), data_path, output_directory]

	elif script_name.endswith('.R'):
		command = ["Rscript", str(script), data_path, output_directory]

	else:
		print ("Current verstion accept just python and R files.")
		return

	try:
		subprocess.run(command, check=True)
	except (OSError, subprocess.CalledProcessError) as exc:
		print ("Error in executing the script " + script_path + " on " + data_path)
		print(exc)

#==========================================================================#
def pre_selection (data_path, script_name = ""):

	if not Path(data_path).exists():
		print ("Error: data path does not exist")
		sys.exit(1)

	data_name = Path(data_path).stem
	output_directory = Path('results/pre_selection') / data_name

	output_directory.mkdir(parents=True, exist_ok=True)

	graphs_path = Path("src/pre_selection")

	if script_name == "":
		graph_names = [fn for fn in graphs_path.iterdir()
              if fn.suffix in ['.py', '.R']]

		for script in graph_names:
			execute_script(data_path, str(output_directory), str(script))

	else:
		execute_script(data_path, str(output_directory), script_name)


#==========================================================================#
def selection (data_path, script_name = ""):

	if not Path(data_path).exists():
		print ("Error: data path does not exist")
		sys.exit(1)

	data_name = Path(data_path).stem
	output_directory = Path('results/selection') / data_name

	output_directory.mkdir(parents=True, exist_ok=True)

	reduction_methods_path = Path("src/selection")

	if script_name == "":
		reduction_methods = [fn for fn in reduction_methods_path.iterdir()
              if fn.suffix in ['.py', '.R']]

		for script in reduction_methods:
			execute_script(data_path, str(output_directory) + "/", str(script))

	else:
		execute_script(data_path, str(output_directory) + "/", script_name)

#==========================================================================#
def prediction (data_path, script_name):

	if not Path(data_path).exists():
		print ("Error: data path does not exist")
		sys.exit(1)

	data_name = Path(data_path).stem
	output_directory = Path('results/prediction') / data_name

	output_directory.mkdir(parents=True, exist_ok=True)

	selection_files_path = Path("results/selection") / data_name

	script_name = Path(script_name).name

	if script_name == "":
		for script in ["var_shrinkage.py", "auto_arima.py", "lstm.py", "vecm.py"]:
			prediction(data_path, script)

	elif script_name in ['var_shrinkage.py', 'auto_arima.R', 'auto_arima.py']:
		execute_script(data_path, str(output_directory), str(Path("src/prediction") / script_name))

	elif script_name in ['lstm.py', 'vecm.R', 'vecm.py']:
		execute_script(str(selection_files_path) + "/", str(output_directory), str(Path("src/prediction") / script_name))

	else:
		print ("Prediction script not found.")

#==========================================================================#
def pre_evaluation (data_path):

	data_name = Path(data_path).stem

	if not Path(data_path).exists():
		print ("Error: data path does not exist")
		sys.exit(1)

	output_directory = Path("results/pre_evaluation") / data_name
	shutil.rmtree(output_directory, ignore_errors=True)
	output_directory.mkdir(parents=True, exist_ok=True)

	script = "src/pre_evaluation/pre_evaluation.py"

	subprocess.run([sys.executable, script, data_path, str(output_directory)], check=True)

#==========================================================================#
def evaluation (data_path):

	data_name = Path(data_path).stem

	if not Path(data_path).exists():
		print ("Error: data path does not exist")
		sys.exit(1)

	output_directory = Path("results/evaluation") / data_name
	output_directory.mkdir(parents=True, exist_ok=True)

	scripts = glob.glob ("src/evaluation/*.py")

	for script in scripts:
		subprocess.run([sys.executable, script, data_path, str(output_directory)], check=True)

#==========================================================================#
if __name__ == '__main__':

	parser = argparse. ArgumentParser ()
	parser. add_argument ("data", help = "data path")
	parser. add_argument ("--type", '-t', help = "task to perform", choices = ["pre_selection", "ps", "selection", "s", "prediction", "p", "pre_evaluation", "pe", "evaluation", "e"])
	parser. add_argument ("--script", "-s", help = "script path", default = "")
	args = parser.parse_args()

	# pre_selection step : computing the causality graphs
	if args.type in ['pre_selection','ps']  :
		pre_selection (args.data, args.script)

	# feature selection / dimension reduction
	elif args.type in ['selection', 's']:
		selection (args.data, args.script)

	# prediction
	elif args.type in ['prediction', 'p']:
		prediction (args.data, args.script)

	# pre_evaluation : compute rmse and mase
	elif args.type in ['pre_evaluation', 'pe']:
		pre_evaluation (args.data)

	# make evaluations: compare methods and models
	elif args.type in ['evaluation', 'e']:
		evaluation (args.data)

	else: print ("Error, unrecognized task name.")
