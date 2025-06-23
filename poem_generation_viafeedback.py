from langchain_ollama import ChatOllama
import re
import sys
import time
import json
from tqdm import tqdm

import poemfeedback
from evaluators import generalSingleEvaluator
poetry_evaluator = generalSingleEvaluator()
poetry_evaluator.load_model()



ordinals = "first second third fourth".split()

MAX_ITERATION_NUMBER = 10
NUMBER_OF_RUNS = 5

nlines_possibilities = [4,7,8,14]
nsyllables_possibilities = [0,8,10,13]

topics = []
topics.append("")
topics.append(" about love")
topics.append(" about death")
topics.append(" about nature")
topics.append(" about router")
topics.append(" about briefcase")
topics.append(" about garbage")

gen_temperatures = []
gen_temperatures.append(0.0)
gen_temperatures.append(0.1)
gen_temperatures.append(0.7)

gen_models = []
gen_models.append("llama3.1")
gen_models.append("gemma2")

analyzers = []
analyzers.append("erato")
analyzers.append("llama3.1")
analyzers.append("gemma2")

#nsyllables = nsyllables_possibilities[0]
#nlines = nlines_possibilities[0]
#topic_str = topics[0]
#gen_temperature = gen_temperatures[0]
#gen_model = "llama3.1"
which_analyzer = analyzers[0]

combinations = [(nsyll, nlin, topic, temp,gen_model) for gen_model in gen_models for temp in gen_temperatures for topic in topics for nlin in nlines_possibilities for nsyll in nsyllables_possibilities]
combinations = [(el1,4,el3,el4,el5) if el1!=0 else (el1,el2,el3,el4,el5) for el1,el2,el3,el4,el5 in combinations]
combinations = sorted(list(set(combinations)))

def name_from_tuple(tp, analyzer):
    topic = ""
    if tp[2]!= "":
        topic = tp[2].split(" ")[2]
    return "analyzer={0}-nsyll={1}-nlin={2}-topic={3}-temp={4}-genmodel={5}-".format(analyzer,tp[0],tp[1],topic,tp[3],tp[4])

n_exps=0
for combination in combinations:
    gen_temperature=combination[3]
    if gen_temperature == 0.0:
        number_of_runs = 1
    else:
        number_of_runs = NUMBER_OF_RUNS
    for nun_number in range(number_of_runs):
        n_exps+=1

#combinations = [[0,4, " about death", 0.0],[8,4," about nature",0.7],[0,8," about love",0.0]]

for expnumber,combination in enumerate(combinations[:5]):
    print ("###################")
    print ("COMBINATION NO: ",expnumber)
    print ("NUMBER of COMBINATIONS: ",len(combinations))
    print ("MAX NUMBER EXPERIMENTS: ",n_exps)
    print ("###################")

    timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
    filename  = name_from_tuple(combination,which_analyzer)

    nsyllables = combination[0]
    nlines = combination[1]
    topic_str = combination[2]
    gen_temperature=combination[3]
    gen_model = combination[4]

    conf = {"nlines":nlines,"nsyllables":nsyllables,"topic_str":topic_str,"gen_temperature":gen_temperature,"gen_model":gen_model,"which_analyzer":which_analyzer}


    if gen_temperature == 0.0:
        number_of_runs = 1
    else:
        number_of_runs = NUMBER_OF_RUNS

    for nun_number in range(number_of_runs):

        llm = ChatOllama(
            model=gen_model,
            temperature=gen_temperature,
            # other params...
        )

        if which_analyzer == "erato":
            analyzer = poemfeedback.erato_analyzer_object()
        elif which_analyzer == "llama3.1" or which_analyzer == "gemma2":
            analyzer = poemfeedback.llm_analyzer_object(llm=which_analyzer)
        else:
            print ("Write the right analyzer")
            exit(-1)




        #nlines
        if nsyllables == 0:
            first_prompt = 'Please create a poem. The poem should contain '+str(nlines)+' lines'+topic_str+'. Return only the poem, nothing else.'
        else:
            first_prompt = 'Please create a poem. The poem should contain 4 lines with '+str(nsyllables)+' syllables each'+topic_str+'. Return only the poem, nothing else.'

        messages = [
            ("human",first_prompt),
        ]

        acceptable = False

        iterationno = 0

        ai_msg = llm.invoke(messages)
#        print (ai_msg.content)

        current_result = ai_msg.content.strip()
        messages.append(("assistant", ai_msg.content))


        while (not acceptable) and iterationno<MAX_ITERATION_NUMBER:

            fw = open("output/"+filename+"run_number="+str(nun_number)+"-poem-iterationnumber="+str(iterationno), "w")
            fw.write(current_result)
            fw.close()

            current_resultv = current_result.split("\n")
            analysis,enteredpoem = poetry_evaluator.analyze_lines(current_resultv)

            fw = open("output/"+filename+"run_number="+str(nun_number)+"-poem-iterationnumber="+str(iterationno)+".analysis", "w")
            fw.write(json.dumps(analysis))
            fw.close()

            if nsyllables == 0:
                #Condition and feedback for nlines:
                result_nlines = analyzer.analyze(current_result, analysis_type="nlines")
                if result_nlines == nlines:
                    acceptable = True
                    messages.append(("human","Thank you!"))
                    ai_msg = llm.invoke(messages)
                    current_result = ai_msg.content.strip()
                    messages.append(("assistant", ai_msg.content))
                else:
                    feedback = 'The poem doesn’t have '+str(nlines)+' lines, it has '+str(result_nlines)+' lines. Can you create a poem with '+str(nlines)+' lines? Return only the poem, nothing else.'
                    #I needed to add the "Can you create...". Without that the LLM would say, you are right, it is not correct.
            else:
                #Condition and feedback for nlines:
                result_nlines = analyzer.analyze(current_result, analysis_type="nlines")
                if result_nlines == nlines:
                    result_nsyllables = analyzer.analyze(current_result,analysis_type="nsyllables")
                    if result_nsyllables == [nsyllables]*nlines:
                        acceptable = True
                        messages.append(("human","Thank you!"))
                        ai_msg = llm.invoke(messages)
                        current_result = ai_msg.content.strip()
                        messages.append(("assistant", ai_msg.content))
                    else:
                        resultperline = [result_nsyllables[ind]==nsyllables for ind in range(len(result_nsyllables))]

                        feedback = ""
                        for indres,res in enumerate(resultperline):
                            if not res:
                                feedback+= "The number of syllables in the "+ordinals[indres]+" line is "+str(result_nsyllables[indres])+" and it should have been "+str(nsyllables)+". "
                        feedback += "Can you create a poem with the right number of syllables? Return only the poem, nothing else."
                else:
                    feedback = 'The poem doesn’t have '+str(nlines)+' lines, it has '+str(result_nlines)+' lines. Can you create a poem with '+str(nlines)+' lines? Return only the poem, nothing else.'

            if not acceptable:
                messages.append(("human",feedback))
                ai_msg = llm.invoke(messages)
    #            print (ai_msg.content)
                current_result = ai_msg.content.strip()
                messages.append(("assistant", ai_msg.content))

    #            print ("ITERATION!",iterationno)
    #            print (poemfeedback.pretty_print_prompt(messages))

                iterationno += 1

        fw = open("output/"+filename+"run_number="+str(nun_number)+"-configuration", "w")
        fw.write(json.dumps(conf))
        fw.close()

        fw = open("output/"+filename+"run_number="+str(nun_number)+"-interaction", "w")
        fw.write(timestamp+"\n")
        fw.write(poemfeedback.pretty_print_prompt(messages))
        fw.close()
        #print (poemfeedback.pretty_print_prompt(messages))