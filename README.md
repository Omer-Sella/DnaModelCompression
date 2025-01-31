# dna_archival_storage
This repository builds on the brilliant work of [Jasmine Quah](https://github.com/jasminequah)
## Setup
To clone repository and submodules:
```
git clone --recursive https://github.com/jasminequah/dna_archival_storage
cd dna_archival_storage
git clone https://github.com/Omer-Sella/turboDNA
```

If running basic simulation (no basecalling), only standard libraries used.

If running simulation with raw signal simulation using Scrappie & Bonito basecalling, run `./setup.sh` first. A GPU is required to run the Bonito basecaller.


## Simulator Usage
Two modes of error simulation are currently available: one using given error rates and the `error_simulation` package (see below for more detail), and the other using Scrappie for signal generation and Bonito basecalling.

In Python, to run the simulation:
```
from simulation import simulate_errors
simulate_errors('AGGAATCTAGGCAGTAATAAATACATCAATCAATCAACTTAGCTATGCATTCATGAATAG', True)
```
Pass `True` for the second parameter to run the basic simulation (default), and `False` to run the simulation using Scrappie and Bonito.

### `error_simulation`
This package is used to simulate simple synthesis and sequencing errors on a nucleotide sequence for the basic simulation. It builds upon the work from a previous MEng student's project to model these errors. It uses the error profiles defined in their project report, which may not be accurate. It also assumes indels & substitution errors are iid among the sequence.

### Scrappie & Bonito simulation:
Simulates synthesis errors using same method as before, but simulates generated signals from sequencing process using Scrappie for R9.4.1 pore & basecalls these using Bonito basecaller with CTC architecture. More detail can be found in report.

The simulator is also capable of simulating a user-specified error rate using the following:
```
simulate_errors('AGGAATCTAGGCAGTAATAAATACATCAATCAATCAACTTAGCTATGCATTCATGAATAG', False, error_rate=<ERROR_RATE>)
```

If you wish to only simulate substitution errors, use the following:
```
simulate_errors('AGGAATCTAGGCAGTAATAAATACATCAATCAATCAACTTAGCTATGCATTCATGAATAG', False, no_indels=True)
```

Lastly, the simulator generates intermediate FAST5, FASTQ and FASTA files, which are removed after the simulation is complete. If you wish to keep these intermediate files, specify a `save_dir` as follows:
```
simulate_errors('AGGAATCTAGGCAGTAATAAATACATCAATCAATCAACTTAGCTATGCATTCATGAATAG', False, save_dir=<OUT_PATH>)
```


## Reproducing results from project experiments:

### Simulator evaluation:
```
from simulation import evaluate_simulator
evaluate_simulator(seq_length=300, runs=500, outdir=<OUT_PATH>)
```
This will generate and save files containing error statistics and error characterisation to the `<OUT_PATH>` specified for 500 simulated sequences of length 300nt.


### Pruning experiments:
To reproduce the pruning experiments, make sure you follow the instructions in the bonito repo to download their training dataset.

Run the following command:
```
bonito compress --pretrained dna_r9.4.1@v3.2 --weights 1 --batch 32 --directory bonito/bonito/models/na_r9.4.1 --epochs 5 --prune_level=<AMOUNT_TO_PRUNE_EACH_ITERATION> --pruning_iterations=<NUM_PRUNING_ITERATIONS> <MODEL_OUTPUT_DIR>
```
To perform one-shot pruning, set `<NUM_PRUNING_ITERATIONS> = 1`. The argument passed to `--directory` is the location of the training data.

Global unstructured pruning is performed by default. To perform structured pruning, pass `--structured` as an additional parameter.


Finetuning the pruned models is then done by running:
```
bonito train --pretrained <MODEL_OUTPUT_DIR> --weights <MODEL_WEIGHTS_SUFFIX> --batch 32 --directory bonito/bonito/models/na_r9.4.1 <FINETUNED_MODEL_OUTPUT_DIR>
```
Here, if your model weights are saved as `weights_3_1.tar`, set `<MODEL_WEIGHTS_SUFFIX> = 3_1`.


To evaluate model accuracy, use the following command:
```
bonito evaluate <MODEL_DIR> --weights <MODEL_WEIGHTS_SUFFIX> --chunks 0 --directory bonito/bonito/models/na_r9.4.1 --batchsize 32
```
If you find you are running out of memory during execution of the above command, try reducing batch size or using `--chunks 1000` to reduce the amount of data used for evaluation.

A handful of our pruned models can be found on the `models` branch of our bonito fork [here](https://github.com/jasminequah/bonito/tree/models/bonito/models/pruned_models).


### Error correcting code experiments:
Encoding data with error correcting codes:
```
from encode import test_ecc
test_ecc(data='encoding_data/data_short.txt', rate=<CODE_RATE>, error_rate=<CHANNEL_ERROR_RATE>, short_oligos=<SHORT_OLIGOS>)
```
This will encode the data file into DNA sequences using the code with rate `<CODE_RATE>`, simulate errors with error rate `<CHANNEL_ERROR_RATE>`, then decode the read sequences. At the end of its execution, it will print out the percentage of insertion, deletion and substitution errors.

`<CODE_RATE>` can be set to `'1/3'`,`'1/2'` or `'2/3'`.

`<SHORT_OLIGOS>` can be set to `True` or `False`, depending on whether you want the data to be stored in oligos of length 150nt or 300nt respectively.


### Sparse matrix multiplication experiments:
Run the following script:
```
python3 sparse_experiments.py
```
This generates and saves a figure showing the relationship between sparsity of a sparse tensor in Pytorch and the latency taken for sparse-dense matrix multiplication with that sparse tensor on both CPU and GPU (if available).

## TODOs:
* Implementation of Smith Waterman alignment has bug when aligning read sequence consisting of one base, eg: `GTTTGGACAATCTCGGCGTGTTCTATTCTCTGGCCCGAATCGAGTCTGCCTACTACCTCTCGGCTCCTTTGCATACCTCAGAGAACGACCCCTATCCCTG` and `C`.
* Rather than using our implementation of Smith Waterman alignment, switch to using version implemented by parasail library. This performs alignment much faster by using vectorised operations.

Also see [WIP branch](https://github.com/jasminequah/dna_archival_storage/tree/wip) for some WIP code which may be useful.
