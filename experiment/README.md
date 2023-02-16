### experiment

The results of our experiments.

- `comparison_experiment`: the comparison experiment of NFTGuard with other 6 tools (i.e., Mythril, Oyente, Sailfish, Securify1, Securify2, and Smartian).

  - `results_1000`: source outputs of the 6 tools.
  - `contracts_1000.zip`: dataset for conducting the comparison experiment.
  - **`issuetype_paperortool.csv`**: the collected **papers/tools** from conferences/journals of **software** and **securiy** with **issue types** they support to detect.

- `evaluation`: evaluation results of NFTGuard.

  - `false_positives` and `false_negatives`: analysis and cases of false positives and false negatives of NFTGuard.
  - `resampled_evaluation`: labeled results on the resampled dataset with a confidence interval of 10.

- `solutions`: cases of problematic code samples (**toy samples** and **real cases** that were correctly reported) and contracts **fixed with applied solutions**.
- `100_label.csv`: label results of 100 randomly selected samples in our original experiment (not by a confidence interval).
- `Dataset.zip`: source code of 16,527 NFT smart contracts in our dataset.
- `NFTContractDefects.csv`: detection result of 16,527 NFT smart contracts by NFTGuard.
