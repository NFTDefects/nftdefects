# NFTDefects

This is the repository of our work on the *Definition and Detection of Defects in NFT Smart Contracts*, accepted by [ISSTA '23](https://2023.issta.org/details/issta-2023-technical-papers/23/Definition-and-Detection-of-Defects-in-NFT-Smart-Contracts).
Please **go to** each directory for further information (with a `README` markdown file per directory).

### NFTGuard

The source code of our tool with a detailed `README`.

### defects_definition

The dataset that we use to define the 5 defects. The `defect_map.csv` stores the mapping relationship between inputs (i.e., posts and reports) and the 5 defect types.

### experiment

The results of our conducted experiments.

- Comparison with the other 6 tools (with outputs of them).
  - collected papers/tools and issue types they support to detect (see csv file).
  - output of the tools.
- Results of large-scale experiment on 16,527 NFT smart contracts.
- Evaluation results of related experiments.
  - labeled results on randomly sampled dataset with a confidence interval of 10 and a confidence level of 95% for **precision** and **false positives** evaluation.
  - analysis of **false negatives** by the same sampling approach on contracts where no defect was reported.
- Effectiveness evaluation of **proposed solutions** for each defect, which shows that after apply the suggested solutions, NFTGuard will not incorrectly report them.
