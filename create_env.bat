@echo off

rem Create the Conda environment
conda create --name Rec-skills -y

rem Activate the environment
conda activate Rec-skills


rem Check if GPU is available
where nvidia-smi > nul
    if %errorlevel% equ 0 (
        rem GPU is available, install GPU version
        conda install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia -y
    ) else (
        rem GPU is not available, install CPU version
        conda install pytorch cpuonly -c pytorch -y
    )

rem Install other packages from requirements.yml
rem conda env update --name Rec-skills --file requirements.yml -y

rem Install python kernel to run jupyter notebook
conda install -c anaconda ipykernel -y
python -m ipykernel install --user --name=Rec-skills
