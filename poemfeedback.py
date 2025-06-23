from langchain_ollama import ChatOllama
from evaluators import generalSingleEvaluator

from tqdm import tqdm
import re

def flatten(l):
    return [subel for el in l for subel in el]

def pretty_print_prompt(lst):
    return_txt = ""
    for sender, msg in lst:
        return_txt += " > "+sender+": "
        return_txt += msg
        return_txt += "\n"
    return return_txt

prompt_lines = "How many lines do the following poems have? Think step by step and at the last line return the number between square brackets."
#prompt_lines = "How many lines do the following poems have? Return the number between square brackets."

prompt_syllables = '''Syllable is a unit of pronunciation having one vowel sound, with or without surrounding consonants, forming the whole or a part of a word. Count the number of syllables in the given sentence and return the number between square brackets: '''

poem = '''thou wilt not harmonize me blend alone
meanwhile, impatient to verbalize and tone
they expose come to compromise your life
the reluctant exteriors of belt

never blend the fire inside you harmonize
his cold crown and alienated place
and reasonable drops his sound face
and hurl it him, verbalize a transfusion

it's why you subtitle to render there
sound its clothing, reasonable its fare
just say a chance to verbalize myself
for miserable reliefs that break with self

compromise at me, expose what i mean
ooh interpret that girl, render that scene'''

poem = '''I have been here before,
But when or how I cannot tell:
I know the grass beyond the door,
The sweet keen smell,
The sighing sound, the lights around the shore.
You have been mine before,–
How long ago I may not know:
But just when at that swallow’s soar
Your neck turned so,
Some veil did fall,–I knew it all of yore.
Then, now,–perchance again!
O round mine eyes your tresses shake!
Shall we not lie as we have lain
Thus for Love’s sake,
And sleep, and wake, yet never break the chain?'''


class basic_analyzer_object(object):
    def __init__(self):
        pass

    def analyze(self, poem, analysis_type='nlines', verbose=False):
        if analysis_type == 'nlines':
            pass
        elif analysis_type == "nsyllables":
            pass


        return result

class erato_analyzer_object(object):
    def __init__(self):
        self.poetry_evaluator = generalSingleEvaluator()
        self.poetry_evaluator.load_model()

    def analyze(self, poem, analysis_type='nlines', verbose=False):
        if analysis_type == 'nlines':
            poemv = poem.split("\n")
            analysis,enteredpoem = self.poetry_evaluator.analyze_lines(poemv)
#            print (analysis)
#            print ("N lines: ",type(analysis['linecount']),analysis['linecount'])
            result = sum(analysis['linecount'])
        elif analysis_type == "nsyllables":
            poemv = poem.split("\n")
            analysis,enteredpoem = self.poetry_evaluator.analyze_lines(poemv)
#            print (analysis)
            result = flatten(analysis['No. of syllables per line'])

        return result

class llm_analyzer_object(object):

    def __init__(self, llm="llama3.1"):
        self.llm = ChatOllama(
            model=llm,
            temperature=0,
            # other params...
        )

        self.pattern_line = r"\[(\d+)\]"



    def analyze(self, poem, analysis_type='nlines', verbose=False):
        if analysis_type == 'nlines':
            messages = [
                ("system",prompt_lines)
            ]
            ai_msg = self.llm.invoke(messages + [("human",poem)])
            result_match = re.search(self.pattern_line,ai_msg.content)
            result = int(result_match.string[result_match.start()+1:result_match.end()-1])
            if verbose:
                print ("PROMPT!")
                print (pretty_print_prompt(messages + [("human",poem)]))
                print ("RESPONSE!")
                print (ai_msg.content)
                print ()
                print ()
        elif analysis_type == "nsyllables":
            messages = [
                ("system",prompt_syllables)
            ]
            poem_lines = poem.split("\n")
            result = []
            for line in tqdm(poem_lines):
                if line: #If I send this prompt without a line, it counts the number of syllables of the prompt
                    ai_msg = self.llm.invoke(messages + [("human",line)])
                    result_match = re.finditer(self.pattern_line,ai_msg.content)
                    if verbose:
                        print ("PROMPT!")
                        print (pretty_print_prompt(messages + [("human",line)]))
                        print ("RESPONSE!")
                        print (ai_msg.content)
                        print ()
                        print ()

                    for results in result_match:
#                        print (results)
                        lastresult = results
                    result_inline = int(lastresult.string[lastresult.start()+1:lastresult.end()-1])
                    result.append(result_inline)
        return result

if __name__ == "__main__":
    import sys
#    f=open(sys.argv[1])
#    poem_content = f.read()
#    f.close()

#    print ("Write the poem:")
#    sent = input()
#    results = []
#    while sent:
#        line = sent.strip()
#        llm_analyzer = llm_analyzer_object(llm="gemma2")
#        result = llm_analyzer.analyze(sent, analysis_type="nsyllables", verbose=False)
#        results.append((line,result))
#        sent = input()

#    for line,result in results:
#        print (line,result)

#    print (",".join([str(res[1][0]) for res in results]))

    llm_analyzer = llm_analyzer_object(llm="llama3.1")
    print (llm_analyzer.analyze(poem, analysis_type="nlines", verbose=False))

#    erato_analyzer = erato_analyzer_object()
#    print (erato_analyzer.analyze(poem, analysis_type="nlines"))


