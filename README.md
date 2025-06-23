# llmgen_poetry_feedback

### The dataset

In the folder "dataset" you can find the prompts, interactions and poems from this work. Please check the section `Steps to create the repository` in order to generate the dataset on your own as well.

An example:

The dataset folder contains a number of files that follow a specific name pattern. For instance, there is a file called `analyzer=llama3.1-nsyll=10-nlin=4-topic=death-temp=0.7-genmodel=gemma2-run_number=2-interaction`. This file contains the interaction to reach the poem with certain characteristics. This interaction uses "llama3.1" as the analyzer, and gemma2 as the generator. The goal was to create a poem with 10 syllables per line, 4 lines and the topic was `death`. The temperature employed was 0.7, and as the temperature is different to 0, there are 5 runs that were tested. In this case, this interaction includes the run_number 2.

### Steps to create the repository

Clone the repository

`git clone https://github.com/manexagirrezabal/llmgen_poetry_feedback.git`

Untar the Erato version

`tar xvzf erato_feedbackversion.tgz`

Move the feedback generators to the Erato folder

`mv poem_generation_viafeedback.py erato/`

`mv poemfeedback.py erato/`

Change directory to Erato

`cd erato`

Create output directory

`mkdir output`

Run the system to generate poems using feedback

`python poem_generation_viafeedback.py`