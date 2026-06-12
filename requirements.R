# Some of these packages may can not be installed, but can be installed manually, like rJava and TransferEntropy

packages = c ("NlinTS", "vars", "kernlab")

for (package in packages)
{
  if (!requireNamespace(package, quietly = TRUE))
    install.packages(package, repos = 'http://cran.us.r-project.org')
  library(package, character.only = TRUE)
}
