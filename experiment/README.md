### experiment

The results of our experiments.

- `comparison_experiment`: the comparison experiment of NFTGuard with other 6 tools (i.e., Mythril, Oyente, Sailfish, Securify1, Securify2, and Smartian) in Section 5.4.
  - `contracts_1000`: dataset for conducting the comparison experiment.
  - `results_1000`: source outputs of the 6 tools.
- `resampled_evaluation`: labeled results on the resampled dataset with a confidence interval of 10 claimed in Section 5.3.
- `NFTContractDefects.csv`: detection result of 16,527 NFT smart contracts by NFTGuard claimed in Section 5.2.
- `Dataset.zip`: source code of 16,527 NFT smart contracts in our dataset.
- `false_positives` and `false_negatives`: cases of false positives and false negatives of NFTGuard illustrated in Section 5.3.
- `fixed_with_solutions`: cases of problematic code samples and contracts fixed with applied solutions mentioned in our paper for each defect, all of which were not incorrectly reported by NFTGuard, as illustrated in Section 5.5.
- `100_label.csv`: label results of 100 randomly selected samples in our original paper.
