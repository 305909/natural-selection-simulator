# Computer-Aided Simulation: Natural Selection and Species Extinction Dynamics

##### by Francesco Giuseppe Gillio
###### Department of Control and Computer Engineering (DAUIN)
###### Politecnico di Torino

## Reference Paper
- [Computer-Aided Simulation: Natural Selection and Species Extinction Dynamics](https://github.com/305909/natural-selection-simulator/blob/main/docs/natural-selection-simulator-ACM.pdf)

## Abstract

This research aims to structure a discrete event simulator that replicates the intricate interactions and evolutionary trajectories of various species that co-exist within the same environment. Focusing on the Holocene epoch, approximately 11,650 years ago, the study investigates the different outcomes resulting from the interspecific interactions among distinct species of the genus Homo: Homo sapiens, Homo neanderthalensis, and Homo erectus. Through simulation of historical scenarios, this project explores the dynamics of natural selection and species extinction. With an high-performance simulation framework, the research examines the implications of social structures, cognitive abilities, and resource competition on species survival and extinction rates. The simulator provides critical information on the evolutionary mechanisms and significant factors that led to the decline of non-contemporaneous species. The results of extensive simulations underscore the essential role of social cooperation and strategic alliances in shaping evolutionary outcomes. Ultimately, this investigation not only enriches the understanding of ancient human dynamics but also lays the groundwork for future explorations of evolutionary biology within complex ecological contexts.

## Setup for Google Colab

Clone the repository by running the following command:

```python
!git clone https://github.com/305909/natural-selection-simulator.git
```

#### How to run the code on Google Colab

Simulate natural selection and species extinction dynamics by running the following command:

```python
# set output path directory
OUTPUT = 'results'

# run simulation
!python /content/natural-selection-simulator/src/simulator.py \
        --selections 10000 \
        --timeframe 45 \
        --rate 0.15 \
        --alpha 0.25 \
        --improve 0.5 \
        --lifetime 15 \
        --directory {OUTPUT}
```

For more details, check out the available execution parameters by passing the `--help` argument.
