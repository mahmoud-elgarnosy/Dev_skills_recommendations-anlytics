#!/bin/bash

# Create the Conda environment
conda create --name Rec-skills --yes

# Activate the environment
conda activate Rec-skills

# uncomment these lines to install pytorch
# Check if GPU is available
if [[ -z $(command -v nvidia-smi) ]]; then
    # GPU is not available, install CPU version
    conda install pytorch torchaudio cpuonly -c pytorch --yes
else
    # GPU is available, install GPU version
    conda install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia --yes
fi

# Install other packages from requirements.yml
conda env update --name Rec-skills --file requirements.yml --yes

# Install python kernel to run jupyter notebook
conda install -c anaconda ipykernel
python -m ipykernel install --user --name=Rec-skills