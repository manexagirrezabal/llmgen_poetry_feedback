# llmgen_poetry_feedback

### The dataset



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