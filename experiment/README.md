### experiment

The results of our conducted experiments.

#### Overview

-   Comparison with the other 6 tools (with outputs of them).
    -   collected papers/tools and issue types they support to detect (see csv file).
    -   output of the tools.
-   Results of large-scale experiment on 16,527 NFT smart contracts.
-   Evaluation results of related experiments.
    -   labeled results on randomly sampled dataset with a confidence interval of 10 and a confidence level of 95% for **precision** and **false positives** evaluation.
    -   analysis of **false negatives** by the same sampling approach on contracts where no defect was reported.
-   Effectiveness evaluation of **proposed solutions** for each defect, which shows that after apply the suggested solutions, NFTGuard will not incorrectly report them.

#### Details

-   `comparison_experiment`: the comparison experiment of NFTGuard with other 6 tools (i.e., Mythril, Oyente, Sailfish, Securify1, Securify2, and Smartian).

    -   `results_1000`: source outputs of the 6 tools, labeled results refer to [ReentrancyStudy Dataset](https://github.com/InPlusLab/ReentrancyStudy-Data/tree/main/reentrant_contracts) while none is a TP reentrancy issue.
    -   `contracts_1000.zip`: dataset for conducting the comparison experiment.
    -   **`issuetype_paperortool.csv`**: the collected **papers/tools** from conferences/journals of **software** and **security** with **issue types** they support to detect.

-   `evaluation`: evaluation results of NFTGuard.

    -   `false_positives` and `false_negatives`: analysis and cases of false positives and false negatives of NFTGuard.
    -   `resampled_evaluation`: labeled results on the resampled dataset with a confidence interval of 10.

-   `solutions`: cases of problematic code samples (**toy samples** and **real cases** that were correctly reported) and contracts **fixed with applied solutions**.
-   `100_label.csv`: label results of 100 randomly selected samples in our original experiment (not by a confidence interval).
-   `Dataset.zip`: source code of 16,527 NFT smart contracts in our dataset.
-   `NFTContractDefects.csv`: detection result of 16,527 NFT smart contracts by NFTGuard.
